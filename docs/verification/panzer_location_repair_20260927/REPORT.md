# 同布局seed38开柱复验

2026-09-27。导航飞行源码7380669与视觉集成dd01d8b配套，282项离线回归后，在冻结seed38地图执行一次SITL。

修正障碍柱开启，水平膨胀0.275m（5cm网格有效约0.30m）、上0.20m、下0.10m。默认panzer必须取得精修Hint才参与高位提前TOP3；单帧粗记忆保留。复核无正式候选仅撤销位置，不禁用整类；真实APPROACH失败保留原降级。

结果：三高权重red_cross→bridge→panzer、两门、H降落PASS。高位退出34.984s，第三投98.509s，整场193.650s。上一轮为281.353s且第三投tent，单次同布局节省87.703s（31.17%）。无H错误返访、牛耕补搜、类别降级或首轨迹终端超时，接触/边界/高度违规0。进程收尾零残留，俯视/跟随/合成录像均完整解码通过。

验收边界：单次不代表所有seed成功率。位置退休兜底本轮未触发，由离线回归覆盖；保守全树+底座投影与55cm旋转包络有35个重叠采样、最大分离轴重叠18.3cm，与已选择的中部柱口径不同，不应写成全树冠投影零越过。模拟ACK误差不是实物落点误差。

[完整报告、图表及复现脚本（视觉研究分支）](https://github.com/Qinling-Melon-Farmers/liftrace-visionwork/blob/feat/high-view-search-research/docs/verification/panzer_location_repair_20260927/REPORT.md)。视频留在本机`logs/panzer_location_repair_seed38_20260927_154743`，不入Git。不部署板端、不追加新仿真。
