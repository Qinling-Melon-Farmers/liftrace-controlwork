# 导航研究分支视觉镜像同步（实施：2026-10-04，来源：2026-10-03）

## 来源与实施范围

实施基点：导航 `feat/high-view-liveness-20260919@33f60739`。
配套完整视觉/控制权威版本：
`Qinling-Melon-Farmers/liftrace-visionwork@3721e7ccb12a85041fb4be7010c97ec1f6e7ff5d`。
用户/主代理本轮反馈：视觉研究 `b9778b05`、competition `4bce9f2e`、导航板端参考
`8c131b5f` 已验证、提交并推送。本子任务只修改导航 liveness，不重复检查其他工作树。

远端状态按用户直接 `git ls-remote` 核查订正：导航 origin/liveness 原已是
`33f60739`，origin/板端参考此前已是 `a27852d`，两者均不是漏推。
本地 origin.fetch 仅覆盖 main/旧 VCL06，导致缓存陈旧，普通 fetch 不会刷新未覆盖的
分支；refspec/跟踪修正及本次镜像提交的 origin/fork 推送由主代理处理。
真正此前待推的是视觉最后三笔提交。以上远端结果由用户提供，本子任务未访问远端。

- `bb8877b7`：仅对 `drop_circle/drop_cross` 的 `DropOffset` 复制 header，使用
  `last_seen` 查测高；候选 header、H 路径、证据/ready 生成时间及确认条件保留。
- `8d4cb2df`：H 自适应窗口 31→81，H 暗色掩膜开运算前增加可配置 7 像素闭运算；
  PT/RKNN 在 `landing` 暂停类别推理，离开后恢复，模式跨越的在途结果丢弃。
  门控模块通过 `setup.py`、`catkin_python_setup()` 安装，话题及默认模式可配置。
- `3721e7cc`：仅记录权威来源。本树没有板端试飞监督器，也没有新版 external H
  控制实现，不复制启动器、旧控制包或 legacy 快照。

## 必须保留的差异

现有五类 RKNN metadata/输出契约、历史 split 支持、模型选择、0.75 投递圆环门槛、
其他确认条件、导航策略、位姿连续性保护、速度、测高配置和旧兼容桥默认值均保持。
不引入 `AlignmentTargetContext`、`ReleaseEvidenceContext` 或整套新策略模块。
此旧 H 节点未同步新版 H 阶段门控、笔画 fallback 等历史功能；本次 landing gate
仅指类别检测器。现有 fusion 在 landing 只等待 `landing_detector`，不依赖 YOLO。

本树仍不是完整板端发行包：新版测高消费者、人工 OFFBOARD 启动和外部 H 接管
取消保护须由上述视觉 `3721e7cc` 或其明确回流版本提供。

## 验证

修改前先记录权威版本与移植边界，修改后在本树完成：

- 21 项离线行为测试全部通过：真实旧 `_on_targets` 的观测时间/缓存重发/H 兼容/
  过期拒绝/证据时间 5 项；真实 PT/RKNN `_on_image` 的暂停恢复、在途模式切换
  （含往返）、统一/历史 split/无模型空结果、默认模式/显式关闭门控、fusion 完成条件
  和 launch 接线 11 项；生产 C++ H 几何 5 项。
- H 测试抽取本树未经改写的参数加载、`detectLandingPad`、`validateHStructure`
  方法及成员声明，用参数默认值桩代替 ROS 构造，以系统 OpenCV 4.2/GCC 9.4 和 UBSan
  编译执行。完整 H 与反光缝隙 H 通过，关闭闭运算后反光样本恢复拒绝；背景、普通环、
  分离竖线和实心方块保持阴性。测试不创建 ROS 节点。
- 独立构建只 overlay `/opt/ros/noetic`，生成本树原有 7 个消息；实际
  `landing_detector_node` 及整个 `uav_vision` 构建、安装成功。
  `catkin_python_setup()` 的 devel/安装空间均可加载新 helper 和原消息，安装空间
  导入路径指向本树 `logs/vision_mirror_20261003/install/`。
- 测试使用现有 `rl_drone`；ROS catkin 构建/消息生成按 Noetic 使用系统 Python 3.8，
  未安装任何包。8 个 Python 文件 AST 检查、launch/YAML 接线及 `git diff --check` 通过。
- 首轮测试夹具在 `patch.dict(sys.modules)` 内首次导入 OpenCV，恢复字典后重复加载
  native 模块导致导入失败；已将 OpenCV 预加载移到隔离范围外，随后全部通过。
  实际构建只出现既有 CMake 版本/FindPythonInterp 策略提示。

复现命令（工作目录为本导航树，仅编译/离线单元测试）：

```bash
source /opt/ros/noetic/setup.bash
source /home/xhj/miniconda3/etc/profile.d/conda.sh
conda activate rl_drone
cmake -S vision_ws/src/uav_vision -B logs/vision_mirror_20261003/build \
  -DCMAKE_PREFIX_PATH=/opt/ros/noetic \
  -DCATKIN_DEVEL_PREFIX="$PWD/logs/vision_mirror_20261003/devel" \
  -DCMAKE_INSTALL_PREFIX="$PWD/logs/vision_mirror_20261003/install" \
  -DPYTHON_EXECUTABLE=/usr/bin/python3 -DCATKIN_ENABLE_TESTING=OFF \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build logs/vision_mirror_20261003/build --target install -j2
source logs/vision_mirror_20261003/devel/setup.bash
python -B -m unittest discover -s vision_ws/src/uav_vision/test -p 'test_*.py' -v
```

Windows 宿主执行上述命令须遵守项目 `wsl -e bash -c '...'` 约定。
测试/安装日志位于 `logs/vision_mirror_20261003/`，不进入 Git。

## 源码与测试路径

以下相对于 `vision_ws/src/uav_vision/`，仅 11 个已有源码/配置文件的局部补丁，
3 个新增打包/helper 文件与 3 个适配当前入口的测试：

```text
CMakeLists.txt
setup.py
config/landing_detector.yaml
config/target_detector.yaml
config/target_detector_rknn.yaml
include/uav_vision/landing_detector_node.h
launch/phase_d.launch
launch/phase_d_board.launch
scripts/drop_aligner.py
scripts/target_detector.py
scripts/target_detector_rknn.py
src/landing_detector_node.cpp
src/uav_vision/__init__.py
src/uav_vision/detector_stage_gate.py
test/test_drop_observation_stamp.py
test/test_detector_stage_gate.py
test/test_landing_reflection.py
```

## 未验证与交接

未启动 ROS 节点、SITL、SSH、部署或推送。未验证真实相机反光覆盖率、更多实拍
负样本、GPU/NPU 实际推理、板端时序、H 居中/AUTO.LAND/人工接管或实飞落点。
这些离线测试不能替代完整视觉 `3721e7cc` 配套控制的实机验收。
提交后由用户 review，再由主代理向 origin/fork 推送；不合并 main。
