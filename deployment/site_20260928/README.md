# 2026-09-28 现场部署

当晚追加：现场五组快捷入口的有投递flight已按用户指令选择真实舵机；preview、仅记忆和原八组默认不变。当前等待板端网络恢复后核实服务和坐标，再开始试飞。

**当前五组现场试飞请用 [PREPARATION.md](PREPARATION.md)**：前方6m、左右±1.5m，入口自动加载现场范围并录制bag。八组原始4×4配置保留为默认；不要用不带现场配置的旧命令替代本次入口。

香橙派：orangepi@192.168.156.193。独立目录：

    /home/orangepi/liftrace_board_trials_20260928

源码来自视觉仓 feat/board-deployment-flight-20260920 的 e1f067b（任务代码与 b2185c8 相同），八组测试、导航、视觉、最新高位策略统一构建；模型采用 flight_5cls_20260928_fp16.rknn 与同名五类 metadata。原现场 liftrace_r64_onboard_405bda42 未覆盖，未提交的 release_setpoint_height=0.20、许可范围0.10–0.30已额外备份至 ~/board_deploy_backups/20260928。这是旧入口的 local Z 设置；本八组仍按自动地面参考生成0.60m AGL投递参数，不混用两套高度口径。

## 操作入口

在香橙派每个终端先执行：

    cd ~/liftrace_board_trials_20260928
    source deployment/site_20260928/environment.sh

设备侧MAVROS沿用现场已验证的启动方式。雷达、相机各开一个终端；如果已运行，不要重复启动：

    roslaunch uav_mission mid360_driver2.launch user_config_path:="$PWD/deployment/site_20260928/MID360_config.json"

另一个终端启动相机：

    bash deployment/board_trials_4x4/start_camera.sh /dev/video0

此处MID360 JSON从现场旧工程原样拷贝：雷达192.168.1.175，板端雷达网口192.168.1.100。192.168.156.193是Wi-Fi SSH地址，不替换雷达专用网段。部署检查时eth0为DOWN，尚未验证实时点云输入；应接好原雷达网线并恢复现场既有网口配置，不要在Wi-Fi上绑定雷达地址。

先预览第一组：

    bash deployment/site_20260928/start_test.sh 1 preview

preview只启动定位、地图、视觉和录像，没有飞控设定点出口。关闭preview后，现场需要进行飞行时再执行：

    bash deployment/site_20260928/start_test.sh 1 flight

flight接通控制输出，但不自动解锁或调用任务开始。等待READY、按现场流程操作并确认低空稳定悬停后，在已source环境的另一终端调用：

    rosservice call /navigation/start_mission "{}"

不使用旧整机launch与本入口同时运行。每次新一轮应回到起飞点、机头朝场内，未解锁静置后重新启动应用，自动生成地面基准。

## 八组对应目录

| 目录 | 目的 |
|---|---|
| 01_visual_interrupt | 低空直飞，一次中断、对齐、模拟投递，恢复后原地降落 |
| 02_high_view_revisit | 高位完整一圈，记忆1–3目标，逐个重访模拟投递后降落 |
| 03_h_landing | 到前方H附近，定点升高识别、对齐并降落H |
| 04_corridor_landing | 走廊导航点与避障接H；须先填写现场航点/H |
| 05_low_multi | 低空连续中断、投递、恢复，默认两投后降落 |
| 06_high_priority | 高位TOP3支持条件满足即提前结束，低位重访投递 |
| 07_memory_only | 高位整圈、记忆、下降降落，不投递 |
| 08_full_mission | 高位三投接走廊/H；须先填写现场航点/H |

把示例路径中的01目录替换为相应目录即可。04/08当前航点留空，启动拒绝属于预期行为；本次未把仿真航点填进实机场地。

所有投递专项默认mock，真实舵机无需开启。显式实投入口start_real.sh保留现场 /legacy/Servo_raw 接线，但本次未启动、未调用机构。相机原始/叠加视频、事件与轨迹自动存到 logs/board_<专项>_<时间>/。

## 当前参数

- 本次五组使用前方6m、左右±1.5m；八组原始默认仍为4×4m。起飞固定坐标+X向前、+Y向左，巡航0.5m/s、加速度0.35m/s²。
- 低位1.4m AGL，高位2.6m AGL，投递0.60m AGL；H专项接近1.0m、扫描1.8m。
- 静态map→camera_init，关闭虚拟顶棚，膨胀水平0.25m/上0.20m/下0.10m。
- FAST-LIO特征提取开启，局部地图20m，det_range=6m；高位四组启用修复后的树冠中部障碍柱。
- 五类bridge/panzer/pillbox/tent/red_cross，输出ID0–4。一次有效投影且置信度≥0.60可形成粗线索；提前中断仍需一致观测支持，已取消panzer特判。低空对准与释放条件未放宽。
- 已知相机/槽位参数使用公共known_rig；每轮未解锁静置时自动建立地面基准。

## 部署检查与限制

构建状态和检查记录见本目录CHECKS.json及板端deployment_results。部署期间没有启动ROS应用、解锁、发送任务开始或舵机动作。

NPU已用当前检测器预处理/解码运行真实历史样帧：输出[1,9,8400]，panzer置信度约0.897/0.914，bridge约0.931/0.930，热身后推理约54–57ms。这仅为离线样帧，不是实时全链帧率。当前板端librknnrt=1.6.0、驱动0.9.8，模型Toolkit=2.3.2，存在版本提示；实际输出契约与样帧推理通过，本次未全局替换驱动/运行库。

此前六组SITL中high_view和landing仍有落地终态未完整闭合记录，详见docs/verification/model_five_class_20260928/REPORT.md；本次部署和离线检查不替代实飞验收。默认mock也不能验证真实舵机调用期间的设定点连续性。原包和日志均保留。
