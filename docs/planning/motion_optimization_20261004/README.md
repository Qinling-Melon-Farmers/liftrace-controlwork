# 飞行衔接候选公共接口（2026-10-04）

本导航开发分支先实现共享任务/规划策略，再同步视觉整机候选。默认全部关闭，不改板端冻结版或main；本轮未启动SITL或实飞。

共享 `uav_mission.motion_optimization`、manager、planner_bridge和corridor_speed：投后满足原ACK/控制RUN/对准关闭及新鲜定位后，在最低恢复面允许上升中交接；近墙重访按当前位置/制动储备切换原前视档；路线工具只移除同XY下降对的高点和同高度共线中继；走廊entry_waypoints支持1或2。图像释放门槛和旧控制源码不变。

新增可选参数 `~motion_optimization`：enabled默认false；enabled时manager按SURVEY设置 `/fast_planner_node/search/line_deviation_weight`，桥接使用moving_recovery窗口。新增planner代价非负，碰撞检查不变，不能强制直线。生成前端必须同步给control与bridge设置恢复高度，并给入口/H的指令高度分阶段设置；只同步本模块但不接生成前端不会自动启用优化。没有ROS消息或服务接口变更。

完整配置、相机/FC高度关系、几何图、参数和测试说明：[视觉整机候选](https://github.com/Qinling-Melon-Farmers/liftrace-visionwork/tree/feat/r2026-competition-integrated/docs/planning/motion_optimization_20261004)。现场走廊/H坐标仍须测量。各子项可分别禁用，不要求一次性开启全部。

验证：本工作树24项motion/execution_speed/corridor_speed检查，20通过、4个仅整机前端的测试按预期跳过。共享C++在视觉整机工作树完成实际编译与2项测试；该处uav_mission407项通过，增加manager专测后motion15项通过。未以离线测试冒充整机飞行验收。
