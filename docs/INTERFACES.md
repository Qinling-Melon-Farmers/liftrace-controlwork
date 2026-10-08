

## 2026-10-08 补偿终点不可达反馈

`patrol_control`冻结前复用原NearWallAlignFence判定补偿FC终点。不可达时仍使用`uav_vision/DropAlignmentFeedback`，不增加消息类型：`reason=compensated_target_outside_boundary`，`valid/aligned/frozen=false`；携带原观测时间、完整任务/决策/尝试/槽位/目标身份和未裁剪FC终点。此原因是本次对准已锁存的不可执行事实，不是释放许可，也不代表沿途净空检查。

Planner Bridge从`~target/alignment_feedback_topic`读取；未配置时沿用控制端`/drop_system/alignment_feedback_topic`，最终默认`/uav_vision/drop_alignment_feedback`。只接收当前对准事务的匹配、新鲜报告，原观测不被重新盖时间戳。通过已有CANCEL_PENDING和对准撤销消息请求代理取消，由原ReleaseResult未执行证明结束失败动作并释放槽位预留；已经开始执行或不匹配的报告不得覆盖真实执行事实。保留既有失败候选冷却、预算及后续选点机制，不另建恢复层。
