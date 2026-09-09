# 导航来源：R62首投运行已验证

R64联合结果：固定seed11完整PASS，十seed原始7/10完整PASS；5/7/8存在历史靶板压墙，现已修布设检查但未重跑矩阵。当前完整任务入口/包以liftrace-visionwork的feat/r2026-competition-integrated为准；本分支提供分组源码与报告，不把历史副本当作已独立验收的整机入口。见docs/verification/r64_matrix/REPORT.md。

整机分支8bedcc0已在seed11完成建图、起飞、搜索、panzer第1槽仿真投递和恢复搜索。[运行报告](docs/verification/r62_operational/REPORT.md)。未验证整场或稳定三投；完整复现与打包使用liftrace-visionwork的feat/r2026-competition-integrated。

# 导航来源分支：R61更新

已修复外部标准靶丢标回旧航点，导航配置同步16/21/6cm、9.6m场地与AGL换算；整机验证在liftrace-visionwork的feat/r2026-competition-integrated完成。本轮只有构建/软件回归/静态截图，无新飞行PASS。[R61报告](docs/verification/r61_layout_search/REPORT.md)。两份本地包由精简整机分支打包，不把本来源树中的旧参考装上飞机。

以下保留此前导航来源说明，历史飞行结论不覆盖R61新模型。

> 2026-09-08联合最新结果：R60先导完整PASS37/37，冻结十seed仅2/10完整PASS、8/10三投；全部收尾，不追加仿真，未合main。[报告](docs/verification/r60_full_matrix/REPORT.md) · [失败分析](docs/verification/r60_full_matrix/FAILURE_ANALYSIS.md) · [rqt三图](docs/verification/r60_full_matrix/topology/index.html)。本分支为来源开发checkout，全量复现使用visionwork的feat/r2026-competition-integrated；下文为原开发基线说明，不代表已通过本次鲁棒性验收。

# 无人机导航与控制开发

本分支保留导航工程与原始资产；R60对应导航源码e4a4cc6，整机实际运行源码位于liftrace-visionwork的9cfb3e5。旧包保护快照位于legacy_baseline，机械执行接口与仿真分离。
