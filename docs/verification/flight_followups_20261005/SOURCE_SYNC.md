来源：视觉仓 feat/high-view-route-speed-20261004，公共修复 c832f113，续扫 98038274。按文件三方合入，保留各入口硬件参数及专项差异；所有既有profile均未自动启用续扫。旧控制快照来源：视觉板端分支 f1bd9d3e 的 legacy_baseline/20261005_async_servo。

本导航开发分支不是独立板端发行包。uav_high_view 继续由视觉H/HS完整包提供；本次没有向既有两文件参考目录再增加孤立policy/launch。联调应明确UAV_WS为本导航工作树、VISION_WS为已同步视觉高位工作树，重新source正确devel。新HighViewFull必须使用98038274或后续同补丁SurveyPolicy，不能混用旧视觉overlay。完整独立部署使用整机候选或板端参考分支。

适配验证完成：板端44项（42通过2跳过），整机专项37项（33通过4跳过），整机512项模块隔离回归及Catkin构建通过。详见SYNC.md。
