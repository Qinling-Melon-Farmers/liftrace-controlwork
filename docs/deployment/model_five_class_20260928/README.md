# 五分类实拍强化模型接入（导航研究分支）

视觉实现来源：liftrace-visionwork / feat/high-view-search-research，2026-09-28本轮；没有在导航仓另训一套模型。结果与准确边界见[视觉报告](https://github.com/Qinling-Melon-Farmers/liftrace-visionwork/blob/feat/high-view-search-research/docs/verification/panzer_model_20260928/REPORT.md)。

本分支同步RKNN输出契约、五类metadata及板端视觉入口。图像→class_name的公共消息保持原样；导航任务、槽位服务、飞行速度/阈值均未改动。输出类别bridge/panzer/pillbox/tent/red_cross，red_cross=4，模型无tank输出。

权重单独交付：flight_5cls_20260928.pt / .onnx / _fp16.rknn。板端用RKNN配套config/flight_5cls_20260928_metadata.yaml，不要和旧六类表混用。工具链CPU模拟器可解码，尚未板端NPU实测；旧模型回退需同时指定旧metadata。

八项模块化测试的完整集成源码在本导航仓 **板端参考分支**，来源视觉仓 feat/board-deployment-flight-20260920；它包含相机/视觉与任务接线，不改写试飞组维护的 **板载代码**。本次六组（除两组走廊）4 PASS/2 INCOMPLETE，细节见[板端专项报告](https://github.com/Qinling-Melon-Farmers/liftrace-visionwork/blob/feat/board-deployment-flight-20260920/docs/verification/model_five_class_20260928/REPORT.md)。新模型的框级改进不等于任务事务去重和落地交接已修复。
