# 2026-10-08 导航feature选择性接入

修改前分支：`板端参考分支`，revision `ec672fe84ac6ee3f834ac8f4e4f914f7e86d34fa`。运行源码由整机候选b520ee66基础的本轮修改选择性回流；恢复源为视觉研究62afbef8，速度frame修复回流研究4a3f5244。导航归属map/FSM/traj_server/bridge和恢复共享接口在本仓feature维护；视觉drop_aligner适配仍来自视觉仓权威，未引入实验投影。

本轮接入三类有界恢复（退出虚拟柱/额外膨胀、阶段轻微超高回入），保留原goal/deadline、所有权、独立接收gate，禁止实体/必要净空/未知/场界穿越，不能撤销ABORT。恢复专属child速度按同条完整姿态旋转，普通规划原速度不改。

投递高位恢复原视觉确认后冻结，正确槽位旋转补偿与下降合并，最终4cm/0.05m/s/0.30秒和原许可保留；局部点云净空与边界拒绝不可达目标。H去高位精密运动等待，低位0.35/0.37m、0.08m/s水平、0.10m/s垂直、0.15秒/3条新鲜反馈；未来状态有限暂缓。成功/拒绝时序日志同步。

正式motion/resume默认开启、独立CLI覆盖、生成配置确认；历史validated场地配置不改。恢复仅独立有限场地候选显式开启，正式模板仍关闭。各feature原场地、driver、地图导出与规划配置保留；不复制工作台/低空观察/用户资产。旧控制快照保存于legacy_baseline/20261008/simplified_drop_h_recovery，源于本分支修改前HEAD。

验证：本feature实际生产速度提取10项、H桥接16项及diff检查通过；共用整机候选F与板端候选B视觉/导航完整build及控制142项通过，不能写成本feature独立整包构建。恢复core34/map31/gate9和其它集成验证见视觉仓docs/verification/flight_candidate_simplification_20261008/REPORT.md。B保留原pwm实体包缺失测试的skip；不以跳过代替真实板端链路。

本轮不上板、不运行ROS/SITL、不修改main。本地接口适配已得到用户“本轮一起适配，暂不上板”授权；动态恢复和同场耗时对照待新授权。
