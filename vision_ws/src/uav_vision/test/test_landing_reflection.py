"""Compile/run actual H geometry methods with OpenCV, without a ROS constructor."""
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

import yaml


PACKAGE = Path(__file__).resolve().parents[1]
HARNESS = r'''
#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

namespace uav_vision {
struct DefaultParameters {
  template <typename T>
  void param(const std::string&, T& value, const T& fallback) { value = fallback; }
};
class LandingDetectorNode {
public:
  DefaultParameters nh_;
  PARAMETER_FIELDS
  void loadParameters();
  bool detectLandingPad(const cv::Mat&, cv::Point2f&, float&, cv::Mat&,
      std::vector<std::vector<cv::Point>>&, std::vector<double>&, cv::Rect&);
  bool validateHStructure(const cv::Mat&, const cv::RotatedRect&,
      std::vector<double>&) const;
};
PRODUCTION_METHODS
}

cv::Mat pattern(const std::string& kind) {
  cv::Mat image(240, 320, CV_8UC3, cv::Scalar(255, 255, 255));
  const cv::Scalar black(0, 0, 0), white(255, 255, 255);
  if (kind == "background") return image;
  cv::circle(image, cv::Point(160, 120), 72, black, cv::FILLED);
  cv::circle(image, cv::Point(160, 120), 64, white, cv::FILLED);
  if (kind == "ring") return image;
  if (kind == "solid") {
    cv::rectangle(image, cv::Rect(130, 90, 60, 60), black, cv::FILLED);
    return image;
  }
  cv::rectangle(image, cv::Rect(130, 82, 12, 76), black, cv::FILLED);
  cv::rectangle(image, cv::Rect(178, 82, 12, 76), black, cv::FILLED);
  if (kind != "bars")
    cv::rectangle(image, cv::Rect(130, 114, 60, 12), black, cv::FILLED);
  if (kind == "glare")
    cv::rectangle(image, cv::Rect(158, 112, 3, 16), white, cv::FILLED);
  return image;
}

bool structure(uav_vision::LandingDetectorNode& node, const std::string& kind) {
  std::vector<double> metrics;
  return node.validateHStructure(pattern(kind),
      cv::RotatedRect(cv::Point2f(160, 120), cv::Size2f(144, 144), 0), metrics);
}

bool detect(uav_vision::LandingDetectorNode& node, const std::string& kind) {
  cv::Point2f center;
  float radius = 0;
  cv::Mat mask;
  cv::Rect bbox;
  std::vector<std::vector<cv::Point>> contours;
  std::vector<double> metrics;
  const bool found = node.detectLandingPad(pattern(kind), center, radius,
                                          mask, contours, metrics, bbox);
  if (found && (cv::norm(center - cv::Point2f(160, 120)) > 3.0 ||
                metrics.size() < 4 || metrics[3] < 0.85)) {
    std::cerr << "Unexpected center/quality for " << kind << std::endl;
    std::exit(2);
  }
  return found;
}

#define REQUIRE(condition) do { if (!(condition)) { \
  std::cerr << "failed: " << #condition << std::endl; return 1; } } while (false)

int main(int argc, char** argv) {
  if (argc != 2) return 2;
  uav_vision::LandingDetectorNode node;
  node.loadParameters();
  const std::string test(argv[1]);
  if (test == "defaults") {
    REQUIRE(node.adaptive_block_size_ == 81);
    REQUIRE(node.h_close_kernel_size_ == 7);
  } else if (test == "complete") {
    REQUIRE(detect(node, "complete"));
    node.h_close_kernel_size_ = 1;
    REQUIRE(detect(node, "complete"));
  } else if (test == "glare") {
    REQUIRE(structure(node, "glare"));
    REQUIRE(detect(node, "glare"));
    node.h_close_kernel_size_ = 1;
    REQUIRE(!structure(node, "glare"));
    REQUIRE(!detect(node, "glare"));
  } else if (test == "kernel") {
    node.h_close_kernel_size_ = 6;
    REQUIRE(structure(node, "glare"));
    node.h_close_kernel_size_ = 0;
    REQUIRE(!structure(node, "glare"));
  } else if (test == "negative") {
    for (const std::string kind : {"background", "ring", "bars", "solid"}) {
      REQUIRE(!structure(node, kind));
      REQUIRE(!detect(node, kind));
    }
  } else return 2;
  return 0;
}
'''


class LandingReflectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory(prefix="uav_h_geometry_")
        cls.addClassCleanup(cls.work.cleanup)
        work = Path(cls.work.name)
        header = (PACKAGE / "include/uav_vision/landing_detector_node.h").read_text()
        source = (PACKAGE / "src/landing_detector_node.cpp").read_text()
        fields = header[header.index("  std::string image_topic_;"):header.index("\n};")]
        parameters = source[source.index("void LandingDetectorNode::loadParameters()"):
                            source.index("void LandingDetectorNode::cameraInfoCallback(")]
        geometry = source[source.index("bool LandingDetectorNode::detectLandingPad("):
                          source.index("cv::Mat LandingDetectorNode::drawDebug(")]
        cpp = work / "geometry.cpp"
        cpp.write_text(HARNESS.replace("PARAMETER_FIELDS", fields).replace(
            "PRODUCTION_METHODS", parameters + geometry), encoding="utf-8")
        cls.binary = work / "geometry_test"
        flags = shlex.split(subprocess.check_output(
            ["pkg-config", "--cflags", "--libs", "opencv4"], text=True))
        subprocess.run(["g++", "-std=c++14", "-O1", "-fsanitize=undefined",
                        "-fno-sanitize-recover=undefined", str(cpp), "-o", str(cls.binary),
                        *flags], check=True, capture_output=True, text=True)

    def run_case(self, name):
        result = subprocess.run([str(self.binary), name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_production_defaults_match_yaml(self):
        self.run_case("defaults")
        config = yaml.safe_load((PACKAGE / "config/landing_detector.yaml").read_text())
        self.assertEqual(config["landing_adaptive_block_size"], 81)
        self.assertEqual(config["landing_h_close_kernel_size"], 7)

    def test_complete_h_keeps_center_and_quality_with_repair_on_or_off(self):
        self.run_case("complete")

    def test_reflection_cut_is_repaired_and_disable_restores_rejection(self):
        self.run_case("glare")

    def test_even_and_zero_kernel_are_normalized(self):
        self.run_case("kernel")

    def test_background_ring_disconnected_bars_and_solid_square_stay_negative(self):
        self.run_case("negative")


if __name__ == "__main__":
    unittest.main()
