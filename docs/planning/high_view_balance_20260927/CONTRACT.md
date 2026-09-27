# 高位分级记忆集成（2026-09-27）

导航feature保留HighViewFull所有权，视觉研究分支提供NavigationMemory与SurveyPolicy。此批需配套视觉仓feat/high-view-search-research（c7d4ee0之后本批提交），不能独立拿旧视觉模块运行新manager；最终视觉revision见视觉仓docs/verification/balanced_columns_20260927/REPORT.md。

新增内部API：NavigationMemory.interrupt_hints、resolve_low、support_status；SurveyPolicy增加两帧一致参数与5s/1s/0.5m复看参数。没有修改ROS消息或投递许可接口。新manager在SURVEY使用supported TOP3，在低位用新正式候选解歧，物理地点去重，最多一次换位；仍用原REVISIT/REACQUIRE与三维规划器。

主水平膨胀0.275m（5cm体素实际0.30m），up/down=.20/.10m；研究入口与粗排序栅格配套同步。192项任务检查与86项配套高位组件检查通过；导航/视觉构建和31/38参数预检另随视觉报告记录。此时尚未取得新飞行结果，main和板载代码未覆盖。
