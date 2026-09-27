from pathlib import Path
import os,sys,tempfile,subprocess,json
import roslaunch,rospkg,yaml
from trial_config import TRIAL_FOLDERS
P=Path(__file__).resolve().parents[1];root=P.parents[3]
roslaunch.substitution_args._rospack=rospkg.RosPack(ros_paths=[str(root/'vision_ws/src'),str(root/'patrol_uav_ws-patrol_planner/src'),'/opt/ros/noetic/share','/home/xhj/PX4-Autopilot','/home/xhj/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic'])
rows=[]
for trial in TRIAL_FOLDERS:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable,str(P/'scripts/prepare_simulation.py'),trial,tmp],check=True,capture_output=True)
        settings=yaml.safe_load((Path(tmp)/'settings.yaml').read_text())
        os.environ['SIM_RUN_DIR']=tmp
        cfg=roslaunch.config.load_config_default([(str(P/'launch/simulation.launch'),[f'generated_dir:={tmp}',f'trial:={trial}',f'mode:={settings["mode"]}','model_path:=/test.pt'])],11311,verbose=False)
        nodes={n.name:n for n in cfg.nodes};params={k:v.value for k,v in cfg.params.items()}
        assert nodes['mission_manager'].type=='trial_sim_manager.py'
        assert 'target_detector_rknn' not in nodes
        assert nodes['map_camera_alignment'].type=='static_transform_publisher'
        assert params['/fast_planner_node/sdf_map/virtual_ceil_height']==-.1
        assert 'overview_video_recorder' in nodes and 'trial_recorder' in nodes
        assert not any(n.package=='actuator_pwm' for n in cfg.nodes)
        rows.append(dict(trial=trial,nodes=len(nodes),passed=True))
print(json.dumps(rows,indent=2))
