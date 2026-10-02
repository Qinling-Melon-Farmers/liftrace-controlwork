# 试飞验证看板（flight_workbench）

把现场手册 [docs/deployment/flight_handover_20261001/OPERATIONS.md](../../docs/deployment/flight_handover_20261001/OPERATIONS.md)
里的"6~7 个终端 + 等 READY + 看日志"变成浏览器里的点击操作：SSH 连接、各终端启动、
任务组选择与启动、初始化/READY 监视与回报、飞行日志与板端产物浏览。

> 定位：**操作与观测工具**。它只启动现场既有入口命令，不自动解锁、不自动起飞、不自动
> 调用任务开始、不代替飞手接管、不改板端代码、不把口令写进仓库。
> 工作台里的 READY 只是"应用链就绪"，不是起飞许可，也不是飞行验收结论。

2026-10-02 review 已修复实投确认词、第6组速度、设备失败继续启动、旧遥测判就绪及收尾顺序。
H/走廊/整场已适配人工解锁后的自动时序，**本轮仅本地更新，未上板或实飞**。
具体按钮顺序、切组与更新范围见 [review与现场操作](../../docs/deployment/flight_workbench_20261002/REVIEW_AND_OPERATIONS.md)。

---

## 1. 快速开始

在 WSL（开发机）里运行服务端，浏览器打开提示的地址：

```bash
cd /home/xhj/liftrace-worktrees/r2026-board-vision-tests
bash tools/flight_workbench/start_workbench.sh              # 默认 127.0.0.1:8791
# 或指定端口/自动开浏览器
bash tools/flight_workbench/start_workbench.sh --port 8792 --open
```

依赖只有系统 Python3 + `pexpect` + `pyyaml`（本机 ROS 环境已自带），不需要 ROS、不需要
在板端安装任何东西。

连接板端：

1. 在页面顶栏的**板端地址**下拉里选现场地址（默认 `orangepi@192.168.43.99`），再点「连接」；
   或先用 `--password-file`／环境变量给一次口令：
   ```bash
   ORANGEPI_SSH_PASSWORD=... bash tools/flight_workbench/start_workbench.sh
   bash tools/flight_workbench/start_workbench.sh --password-file ~/.orangepi.pass   # 文件须在仓库外
   ```
2. 口令只留在服务进程内存里，用于自动回应 `password:`/`[sudo] password` 提示；勾选"记住"
   才会写到 `~/.config/liftrace-flight-workbench/profile.json`（0600，不在仓库内）。
3. 地址默认取 `workbench.yaml` 的 `connection.host`（外场当前 `orangepi@192.168.43.99`）。
   下拉里的历史地址来自现场部署记录与项目 memoir，选中即写回本机 profile（不改仓库文件）：

   | 地址 | 出处 |
   |---|---|
   | `orangepi@192.168.43.99` | 外场当前（2026-10-01 第五组实投） |
   | `orangepi@192.168.3.15` | 2026-10-01 现场操作手册 / 九组部署 |
   | `orangepi@192.168.43.59` | 2026-09-28~29 现场（site_20260928） |
   | `orangepi@192.168.156.193` | 2026-09-28 现场部署（当时的新 IP） |
   | `orangepi@10.231.47.193` | 2026-09-20 现场（onboard_obstacle_reference） |
   | `orangepi@192.168.3.126` | 2026-09-20 旧板端（r64 基线） |

   清单外的地址：连接参数对话框里的「host（自定义）」直接填，或改 `workbench.yaml` 的
   `connection.host_options`（新增现场地址时一并补 label 说明出处）。

不带板端也能先看界面（本机预览模式：**只渲染界面，默认拒绝执行任何设备/入口命令**）：

```bash
bash tools/flight_workbench/start_workbench.sh --transport local
# 确实要在本机跑那些命令（自检用）才加： --allow-local-commands
```

---

## 2. 现场怎么用（与手册逐条对应）

| 手册里的终端 | 工作台位置 | 命令（界面会原样显示） |
|---|---|---|
| 1 roscore | 终端 tab「1 · roscore」 | `roscore` |
| 2 MAVROS | 终端 tab「2 · MAVROS」 | `roslaunch mavros px4.launch fcu_url:=/dev/ttyACM0:57600` |
| 3 MID360 驱动 | 终端 tab「3 · MID360 驱动」 | `roslaunch uav_mission mid360_driver2.launch user_config_path:="$PWD/deployment/site_20260928/MID360_config.json"` |
| 4 相机 | 终端 tab「4 · 下视相机」 | `bash deployment/board_trials_4x4/start_camera.sh /dev/video0` |
| 5 舵机（可选） | 「5a · PWM 初始化」「5b · 舵机服务」 | `sudo bash .../init_pwm.sh`、`.../pwm_node1 /Servo:=/legacy/Servo_raw` |
| 6 专项 flight 入口 | 任务组卡片「飞行」按钮 → 终端 tab「6 · 专项 flight 入口」 | `bash deployment/site_20260928/start_test.sh <组号> flight` 等 |
| 7 状态监测 | 右栏状态面板 + 自动探针；终端 tab「7 · 状态监测」可手输命令 | 只读遥测 + 交互 shell |

所有终端都会先 `cd <工程根>` 并 `source deployment/site_20260928/environment.sh`，与手册
"每个新终端都先执行 cd 和 source"一致。

### 2.1 启动顺序

1. 点「单实例检查」：看工程根/环境脚本/模型/录像空间是否就绪、板端是否有 roscore·roslaunch·
   gzserver·px4·mavros 残留、九个模块入口是否齐全，并在有 ROS master 时列出**与专项入口冲突的
   旧应用节点**（这些必须先退出）。
2. 点「一键启动设备」（可选舵机）：按 roscore → MAVROS → 雷达 → 相机 顺序逐个启动并等待就绪
   （`ROS master`、`connected=true`、`/livox/lidar`、`/camera/image_raw` 新鲜）。已经在跑的
   设备节点会被识别为"已在运行"而跳过，不重复叠加。舵机两个终端默认不在自动流程里，需单独点击
   （会复位机构，界面会弹确认）。
3. 对应卡片先选「飞行 flight」模式、勾未解锁/起飞点确认；实投组输入「实投」，
   再点卡片底部「飞行（flight）」及弹窗「确认启动 flight」。设备启动本身不启动专项。
   随后等 READY。右栏阶段灯会走 `启动中 → 初始化中（定位/相机/坐标一致）→ 地图就绪（MAPPING_READY）
   → 就绪（READY）`，并实时显示 `pose_samples`、`camera_info`、`image_seen`、`compressed_fresh`、
   定位一致性原因、`distinct_clouds` 等关键量。**`INITIALIZING`、`MAPPING_READY` 都不等于 READY。**
4. 出现 `fc_lio_disagreement` 时按手册处理：等飞控与 LIO 自行收敛，不要转动机身追数值。
5. READY 后由飞手按现场流程解锁/进 OFFBOARD。现场版本会自动请求 OFFBOARD 并按低空稳定条件
   自动启动任务（时间线显示 `AUTO_MISSION_START True`）。本地更新后的03/04/08也使用自动时序；
   03按实际1.0m起飞高度判稳定，自动时序下不再点「启动任务」。旧板端H仍按旧手动流程，更新前核对版本。
6. 结束时按手册落地停机：点「停止（Ctrl+C）」让 `run_trial.py` 走既有收尾（等 `BAG_CLOSED` 和
   应用退出），再断电。

### 2.2 任务组

- **现场组号 1–6**（`deployment/site_20260928/start_test.sh`）：1 单投中断、2 连续两投、
  3 仅记忆、4 整圈重访投递、5 提前中断重访、6 高速拍摄采集。
  该入口的 `flight` 对投递组会自动走 `start_real.sh`（真实舵机 `/legacy/Servo_raw`），
  记忆组走 `start.sh`；界面会显示当前组是「实投/模拟/无投递」以及是否需要舵机。
- **模块目录 01–09**（`deployment/board_trials_4x4/<目录>/start.sh`）：用于 H 降落（03）、
  走廊（04）、整场（08）等专项。04/08在各自独立 `*_test_area.yaml` 中填写实测走廊航点与H坐标，
  **出厂留空时拒绝启动**。08看板默认模拟投递，三个H流程均不使用30cm终点悬停。
- 每个卡片都能展开「命令预览」，看到将要执行的完整命令（可复制），也可只勾「配置检查」
  跑 `--check-config`（不启动任何节点）。
- 防护：`flight` 必须勾选"飞机已回到起飞点、未解锁、机头朝场内"；实投必须额外输入确认词
  **实投**；同一时刻只允许一个专项入口，重复启动会被拒绝。界面预览的命令会随启动请求一起回传
  后端做一致性校验，**不一致直接拒绝启动**，避免"给人看的命令"和"真正执行的命令"漂移。

### 2.3 初始化 / READY 监控与回报

- 阶段机 + 事件时间线 + 告警（含"应该怎么做"的提示），全部来自 `run_trial.py` 的真实输出
  （`INITIALIZING`/`MAPPING_READY`/`READY`/`FLIGHT_STATUS`/`AUTO_*`/异常栈）。
- READY、失败、上报事件都会即时提示；「声音提醒」打开后 READY/失败会有提示音。
- 「生成回报」把当前阶段、时间线、告警、遥测整理成 Markdown，落到
  `~/.config/liftrace-flight-workbench/reports/`，可复制或下载，用于现场留档/群内回报。
- 操作审计写在 `~/.config/liftrace-flight-workbench/ops.jsonl`（谁在什么时刻启动了哪条命令）。

### 2.4 飞行日志与产物

底部抽屉三个页签：

- **运行日志**：专项入口终端的实时输出（可过滤 `READY`/`FLIGHT_STATUS`/`ERROR` 等关键字）。
- **板端产物**：板端 `logs/board_<专项>_<时间>/` 列表（run_metadata.json、camera_info.json、
  supervisor_result.json、vision_events.jsonl、navigation_pose.csv、bag 索引…），可 tail 预览、
  小文件直接下载。**大 bag（数百 MB）请用 `scp`/`rsync` 在板端原包留存后回传**，工作台不搬大包。
- **操作时间线**：本机侧的操作与阶段事件流水。

---

## 3. 离线自检（不需要板端、不需要 ROS）

```bash
cd tools/flight_workbench
python3 tests/test_status.py     # 29 项：阶段解析、告警节流、就绪判定、命令拼装、地址清单
python3 tests/test_probe.py      # 10 项：板端探针（假 rospy，含"只订阅不下发"边界）
python3 tests/test_review.py     # 16 项：实投请求、速度、编排失败/旧遥测、并发与收尾回归
python3 tests/selfcheck.py       # 23 项：纸板工程端到端（会话→编排→READY→回报→产物→SSE）
python3 tests/smoke_http.py      # 15 项：真起服务，检查接口/静态文件/SSE/安全拒绝/地址切换
```

`tests/fake_board/` 是纸板工程，按 `run_trial.py` 的真实输出格式回放一遍
（`INITIALIZING → MAPPING_READY → READY → FLIGHT_STATUS → STOPPED`），
`tests/fake_board_setup.sh` 可重新生成其中的模块入口与占位文件。

---

## 4. 常见问题

| 现象 | 处理 |
|---|---|
| 连接失败 / `ROOT=MISSING` | 换网络后地址变了；确认 `board_root` 是现场实际部署目录（当前 `/home/orangepi/liftrace_board_trials_20260928`）。 |
| 探针不上线（右上角灰） | 探针需要板端 ROS Python 与已 source 的环境；先确认 `环境脚本` 存在。探针未起来不影响终端操作，只是没有遥测。 |
| 一键启动设备某步失败 | 看该步详情与对应终端输出；roscore 已存在会被跳过，MAVROS 串口按实际接线核对。 |
| 初始化一直不过 | 检查飞机是否**未解锁且静置**、机头是否朝场内 +X、相机原始图/压缩图/CameraInfo 是否齐全；`fc_lio_disagreement` 时等收敛，不要转动机身。 |
| READY 后飞机没动 | 正常：现场版本 READY 后仍需**人工解锁**；解锁后监督器才请求 OFFBOARD 并在低空稳定后启动任务。 |
| 04/08 组一启动就退出 | 走廊航点/H 坐标留空，入口按设计拒绝；补实测坐标后再启动。 |
| 舵机按钮点了没反应 | 5a/5b 需要单独确认；`sudo` 提示会自动填口令（若配置了），也可在终端里手动输入。 |
| 收尾 | 先落地上锁，再「停止（Ctrl+C）」，等应用退出与 `BAG_CLOSED`，确认无 `.bag.active` 再断电。现场1–6组末段是30cm悬停，须飞手落地。 |

---

## 5. 文件与接口

```
tools/flight_workbench/
  workbench.yaml        现场配置：连接、终端表、任务组表、单实例检查、探针话题
  server.py             HTTP API + SSE + 顺序启动编排 + 回报
  wb_ssh.py             SSH/本地会话（常驻终端 + 一次性命令，自动回应口令提示）
  wb_board.py           板端操作：连接自检、单实例检查、探针上传、命令拼装、日志浏览
  wb_status.py          阶段解析、告警提示、就绪判定、回报文本（纯函数，可单测）
  board_probe.py        板端只读探针（只订阅话题/读节点与服务列表，每 1s 打一行 JSON）
  web/                  前端（原生 JS，无 CDN、无构建）
  tests/                离线自检与纸板工程
  start_workbench.sh    启动脚本
```

主要接口（前端消费，便于二次开发）：

- `GET /api/snapshot`：全量状态（连接、终端、任务组、阶段、遥测、编排、告警、时间线、产物）
- `GET /api/events`：SSE，首帧 `hello` 带快照，之后 `out/session/stage/telemetry/alert/timeline/
  trial/orchestration/board/toast`
- `POST /api/connect|config|disconnect`、`POST /api/action/{preflight,start_all,stop_all,
  mission_start,report}`、`POST /api/session/{open,input,close,clear,resize,key}`、
  `POST /api/trial/{start,stop}`、`POST /api/logs/{refresh,tail}`、`GET /api/logs/download`

配置改动（换板、换串口、换视频节点、增减任务组）只改 `workbench.yaml`；不要把口令写进仓库。

## 6. 已知限制

- 界面上的"命令预览"是前端按同一规则复刻的字符串（启动时会与后端逐字校验，不一致即拒绝启动）；
  若后端 `build_group_command` 改了写法，前端预览会先被拒绝而不是静默执行错误命令，此时更新
  `web/app.js` 的 `groupCommandBody()` 即可。
- 大 bag（数百 MB）仍需 `scp`/`rsync` 回传；工作台只做 tail 与小文件下载。
- 终端输出按帧批量解析，单帧超两万行的暴输出会短暂卡顿；每会话缓冲 5000 行。
- 尚未接 PTY resize（面板尺寸变化不会同步 `stty`）；声音提示需要一次用户点击后才能播放。
- 板端大文件与 ROS 日志仍由现场既有流程收集，工作台不改板端任何文件（只上传只读探针到
  `logs/flight_workbench/`）。
