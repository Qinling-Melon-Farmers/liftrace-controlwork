> 2026-09-08联合最新结果：R60先导完整PASS37/37，冻结十seed仅2/10完整PASS、8/10三投；全部收尾，不追加仿真，未合main。[报告](docs/verification/r60_full_matrix/REPORT.md) · [失败分析](docs/verification/r60_full_matrix/FAILURE_ANALYSIS.md) · [rqt三图](docs/verification/r60_full_matrix/topology/index.html)。本分支为来源开发checkout，全量复现使用visionwork的feat/r2026-competition-integrated；下文为原开发基线说明，不代表已通过本次鲁棒性验收。

# 无人机导航与控制开发

本分支保留导航工程与原始资产；R60对应导航源码e4a4cc6，整机实际运行源码位于liftrace-visionwork的9cfb3e5。旧包保护快照位于legacy_baseline，机械执行接口与仿真分离。
