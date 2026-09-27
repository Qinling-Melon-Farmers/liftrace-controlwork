# 高位分级记忆集成（2026-09-27）

导航feature保留HighViewFull所有权，视觉研究分支提供NavigationMemory与SurveyPolicy。此批需配套视觉仓feat/high-view-search-research（配套源码74ec4bd5185a7a3a56c40f32f6306ed17f8944dc），不能独立拿旧视觉模块运行新manager；最终视觉revision见视觉仓docs/verification/balanced_columns_20260927/REPORT.md。

新增内部API：NavigationMemory.interrupt_hints、resolve_low、support_status；SurveyPolicy增加两帧一致参数与5s/1s/0.5m复看参数。没有修改ROS消息或投递许可接口。新manager在SURVEY使用supported TOP3，在低位用新正式候选解歧，物理地点去重，最多一次换位；仍用原REVISIT/REACQUIRE与三维规划器。

主水平膨胀0.275m（5cm体素实际0.30m），up/down=.20/.10m；研究入口与粗排序栅格配套同步。192项任务检查与86项配套高位组件检查通过；导航/视觉构建和31/38参数预检另随视觉报告记录。以下已追加同版实跑结果，main和板载代码未覆盖。

## 配套实跑结果

本导航d71b8fe1fdf83873c0b7a2be48167effb984acad＋视觉74ec4bd在开柱、XY0.275m下冻结重跑历史31/38：均三槽/两门/H降落Gate PASS，0包络接触；31为226.723s（red_cross/bridge/panzer），38为281.353s（red_cross/bridge/tent）。38高权重仅2/3，不把降级三投当成最高得分搜索成功。

38有一次bridge首轨迹12s超时，目标局部云未占据；还存在H附近panzer持续误分类与延期/近墙复核多轮预算问题。报告未认定根治。结果归档未修改导航源码、未新增实跑。

详细报告在视觉仓feat/high-view-search-research的`docs/verification/balanced_columns_20260927/REPORT.md`，可从[该分支报告](https://github.com/Qinling-Melon-Farmers/liftrace-visionwork/blob/feat/high-view-search-research/docs/verification/balanced_columns_20260927/REPORT.md)查看；运行视频/原始日志仅保留本机。导航仓仍需配套上述视觉实现，不单独提供完整整机视觉链。
