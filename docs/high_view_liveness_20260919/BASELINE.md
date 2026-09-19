# 研究基线回流导航权威仓
导航分支从 origin/main a182ca9 创建。按文件清单导入视觉集成仓 Qinling-Melon-Farmers/liftrace-visionwork 的 feat/high-view-search-research@778121a 已有 uav_mission 与 Fast-Planner/fast_planner 研究实现；不导入视觉实现、历史报告或模型资产。此前高位策略的导航改动在集成仓演进，本次显式回流，之后新增导航改动先在此分支实现，再按提交同步集成仓。

baseline_files.json列出每个实际变化文件；未整目录覆盖或删除导航独有文件。原planner包按规则14保存于legacy_baseline/20260919，含文件清单与SHA256，不参与编译。高位模块仍通过vision仓的uav_high_view库依赖，未来再拆分所有权；本轮不复制该视觉库到导航仓。

来源已有183项相关回归，导入本身不代表新代码或实机验收。本轮将另行编译/回归后再运行一轮随机场景。
