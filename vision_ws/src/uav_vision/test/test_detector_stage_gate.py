"""Exercise mirror PT/RKNN callbacks with local messages and mocked runtimes."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

import cv2  # Load native modules before patch.dict restores sys.modules.
import numpy as np
import yaml
from sensor_msgs.msg import Image
from std_msgs.msg import String
from uav_vision.detector_stage_gate import DetectorStageGate


PACKAGE = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    # Keep imports independent of GPU/NPU and the system cv_bridge binary ABI.
    with patch.dict("sys.modules", {
        "ultralytics": SimpleNamespace(YOLO=Mock()),
        "cv_bridge": SimpleNamespace(CvBridge=Mock()),
    }):
        spec.loader.exec_module(module)
    return module


PT = load_script("target_detector")
RK = load_script("target_detector_rknn")
FUSION = load_script("detection_fusion")
NAMES = yaml.safe_load(
    (PACKAGE / "config/flight_5cls_20260928_metadata.yaml").read_text())["names"]


class DetectorStageGateTest(unittest.TestCase):
    def make_pt(self, params=None, model_available=True):
        params = dict(params or {})
        params["~model_path"] = "mock-model" if model_available else ""
        model = Mock(names=NAMES)
        model.predict.return_value = [SimpleNamespace(boxes=None)]
        with patch.object(PT.rospy, "init_node"), \
             patch.object(PT.rospy, "get_param", side_effect=lambda k, d=None: params.get(k, d)), \
             patch.object(PT.rospy, "Publisher"), patch.object(PT.rospy, "Subscriber"), \
             patch.object(PT.rospy, "loginfo"), patch.object(PT.rospy, "logwarn"), \
             patch.object(PT, "YOLO", return_value=model):
            node = PT.TargetDetector()
        node._publish_perf = Mock()
        return node

    def make_rk(self, backend="unified", params=None):
        params = params or {}
        def handle(_path, _metadata, tag):
            available = tag == "unified" if backend == "unified" else (
                backend == "split" and tag in ("standard", "tank"))
            return SimpleNamespace(available=lambda: available,
                                   names={0: "tank"} if tag == "tank" else NAMES)
        with patch.object(RK.rospy, "init_node"), \
             patch.object(RK.rospy, "get_param", side_effect=lambda k, d=None: params.get(k, d)), \
             patch.object(RK.rospy, "Publisher"), patch.object(RK.rospy, "Subscriber"), \
             patch.object(RK.rospy, "loginfo"), patch.object(RK.rospy, "logwarn"), \
             patch.object(RK, "CvBridge", return_value=Mock()), \
             patch.object(RK, "_RknnHandle", side_effect=handle):
            node = RK.TargetDetectorRKNN()
        node._bridge.imgmsg_to_cv2.return_value = np.zeros((12, 12, 3), dtype=np.uint8)
        node._infer_handle = Mock(return_value=(self.raw_detection(), .2))
        node._publish_perf = Mock()
        return node

    @staticmethod
    def raw_detection():
        return [{"class_id": 0, "score": .9, "bbox": [0, 0, 10, 10]}]

    @staticmethod
    def frame():
        return Image(height=12, width=12, encoding="bgr8", step=36, data=bytes(432))

    @staticmethod
    def mode(node, value):
        node._stage_gate._on_mode(String(data=value))

    def test_pt_landing_skips_decode_and_inference_then_resumes(self):
        node = self.make_pt()
        self.mode(node, "landing")
        with patch.object(node, "_image_to_bgr", wraps=node._image_to_bgr) as decode:
            node._on_image(self.frame())
            decode.assert_not_called()
        node._model.predict.assert_not_called()
        node._detections_pub.publish.assert_not_called()
        self.mode(node, "disabled")
        node._on_image(self.frame())
        node._model.predict.assert_called_once()
        node._detections_pub.publish.assert_called_once()

    def test_rknn_unified_split_and_empty_resume_without_changing_mapping(self):
        for backend, expected in (("unified", ["bridge"]),
                                  ("split", ["bridge", "tank"]), ("empty", [])):
            with self.subTest(backend=backend):
                node = self.make_rk(backend)
                self.mode(node, "landing")
                node._on_image(self.frame())
                node._bridge.imgmsg_to_cv2.assert_not_called()
                node._infer_handle.assert_not_called()
                node._detections_pub.publish.assert_not_called()
                self.mode(node, "disabled")
                node._on_image(self.frame())
                arr = node._detections_pub.publish.call_args[0][0]
                self.assertEqual([d.class_name for d in arr.detections], expected)
                self.assertEqual(arr.completed_sources, ["target_detector"])

    def test_pt_mode_switch_during_inference_discards_result_even_after_round_trip(self):
        for round_trip in (False, True):
            with self.subTest(round_trip=round_trip):
                node = self.make_pt()
                def infer(*_args, **_kwargs):
                    self.mode(node, "landing")
                    if round_trip:
                        self.mode(node, "disabled")
                    return [SimpleNamespace(boxes=None)]
                node._model.predict.side_effect = infer
                node._on_image(self.frame())
                node._detections_pub.publish.assert_not_called()
                node._publish_perf.assert_not_called()

    def test_rknn_mode_switch_during_unified_and_split_inference_discards_result(self):
        for backend in ("unified", "split"):
            with self.subTest(backend=backend):
                node = self.make_rk(backend)
                def infer(*_args):
                    self.mode(node, "landing")
                    self.mode(node, "disabled")
                    return self.raw_detection(), .2
                node._infer_handle.side_effect = infer
                node._on_image(self.frame())
                node._detections_pub.publish.assert_not_called()
                node._publish_perf.assert_not_called()

    def test_model_unavailable_paths_also_discard_transition_frames(self):
        pt = self.make_pt(model_available=False)
        rk = self.make_rk("empty")
        for node, method in ((pt, "_image_to_bgr"), (rk._bridge, "imgmsg_to_cv2")):
            owner = pt if node is pt else rk
            def decode(*_args):
                self.mode(owner, "landing")
                return np.zeros((12, 12, 3), dtype=np.uint8)
            with patch.object(node, method, side_effect=decode):
                owner._on_image(self.frame())
            owner._detections_pub.publish.assert_not_called()

    def test_default_landing_is_paused_before_first_mode_message(self):
        for factory in (self.make_pt, self.make_rk):
            node = factory(params={"~default_align_mode": "landing"})
            node._on_image(self.frame())
            node._detections_pub.publish.assert_not_called()

    def test_explicit_opt_out_keeps_inference_in_landing(self):
        for factory in (self.make_pt, self.make_rk):
            node = factory(params={"~default_align_mode": "landing",
                                   "~pause_in_landing_mode": False})
            node._on_image(self.frame())
            node._detections_pub.publish.assert_called_once()

    def test_search_and_both_drop_modes_continue_to_infer(self):
        for factory in (self.make_pt, self.make_rk):
            node = factory()
            for mode in ("disabled", "drop_circle", "drop_cross"):
                self.mode(node, mode)
                node._on_image(self.frame())
            self.assertEqual(node._detections_pub.publish.call_count, 3)

    def test_gate_uses_configured_topic_and_repeated_mode_keeps_current_frame(self):
        with patch.object(PT.rospy, "get_param", side_effect=lambda k, d=None:
                          "/test/align_mode" if k == "~align_mode_topic" else d), \
             patch.object(PT.rospy, "Subscriber") as subscribe:
            gate = DetectorStageGate()
        self.assertEqual(subscribe.call_args.args[0], "/test/align_mode")
        epoch = gate.begin()
        gate._on_mode(String(data="disabled"))
        self.assertTrue(gate.current(epoch))
        gate._on_mode(String(data=" landing "))
        self.assertFalse(gate.current(epoch))

    def test_local_fusion_completes_landing_without_target_detector(self):
        node = FUSION.DetectionFusion.__new__(FUSION.DetectionFusion)
        node._align_mode = "landing"
        self.assertTrue(node._bucket_complete({"sources": {"landing_detector"}}))
        node._align_mode = "drop_circle"
        self.assertFalse(node._bucket_complete({"sources": {"circle_detector"}}))

    def test_launch_and_yaml_connect_default_mode_without_changing_legacy_flag(self):
        for name, detector in (("phase_d.launch", "target_detector.py"),
                               ("phase_d_board.launch", "target_detector_rknn.py")):
            launch = ET.parse(PACKAGE / "launch" / name).getroot()
            node = next(n for n in launch.findall("node") if n.get("type") == detector)
            self.assertEqual(node.find("param[@name='default_align_mode']").get("value"),
                             "$(arg default_align_mode)")
            self.assertEqual(launch.find("arg[@name='start_legacy_compat']").get("default"),
                             "true")
            config = yaml.safe_load((PACKAGE / "config" / detector.replace(".py", ".yaml")).read_text())
            self.assertIs(config["pause_in_landing_mode"], True)


if __name__ == "__main__":
    unittest.main()
