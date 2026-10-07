# 导航分支整机运行链选择性同步（2026-10-08）

来源整机F：`f79c2a82e727530f42a371dbf30805b310bbaf8f`（origin/feat/r2026-competition-integrated），修改前本支：`2d0df9378496962c8346bdee997a47fe67bced7e`，分支 `feat/high-view-liveness-20260919`。完整文件选择及每项来源提交/原作者见 SOURCE_SELECTION.json；本地工作树实际更新，保留已有提交历史、原始资产和分支差异。

同步稳定任务生成器/共有硬件session、显式CLI开关和实体舵机包，以及已部署限高保持修复。旧控制修改前快照位于 `legacy_baseline/20261008_competition_release/`，含文件清单和SHA256，不参与编译。消息/服务依赖已随构建验证；舵机后仓释放2100us、锁定1700us、默认被动启动，测试仅用临时mock sysfs。

本支原有 **106** 份YAML/JSON配置按修改前HEAD逐字比较均未变；原硬件入口 `competition_hardware.launch` 原样保留。新增监督器launch为 `competition_supervised_hardware.launch`，独立卡片仍用 `deployment/competition/start.sh`；新入口的共有LIO/规划调参放在 `config/competition/`，不覆盖原现场配置。比赛模板与candidates沿用F正式比赛值，测试场地仅单独示例，门前后Y保留1.0/-0.7/-1.1/-2.5，不设为默认。

CLI保持 `preview|flight --site-config PATH`，可选 `--motion-optimization on|off`、`--obstacle-columns on|off`、`--motion-action-timeout 秒`；省略开关继承YAML，90/120秒预算默认保持。离线校验用 `--check-config`，离线生成可配 `--output-dir PATH --fc-reference X Y Z`。不运行依赖board_trials。

完整-j2源码构建通过；61项相关回归：60通过、1跳过（若跳过，仅因本支不带H工作台测试资产）。四profile各验证两种控制输出模式、两种定位模式与建图展开；CLI帮助/模板preview检查、实体舵机mock CTest、shell语法与git diff检查通过。细项见 TEST_RESULTS.json，日志位于 `logs/competition_release_sync_20261008/`（不提交）。

三线程编译宏与大核绑定已核对；独立入口不接EV预测，不传播新恢复，不要求FC reset方案才验收。板端参考支已有可选EV观察源码保留原貌，本轮未传播/启用。未连接板端，未启动ROS/仿真/执行机构。

版本边界：liveness保留旧视觉算法；本轮只补上下文消息及稳定接口launch。整机投递验收须配套主代理选择的已验收视觉runtime，本地构建不证明视觉实飞等同。 已实飞证据仍是F报告引用的0928/08本地存档与成功metadata，本轮仅证明上述源码构建和离线行为。必要缺件修复限于构建/消息/共有库依赖，不改Fast-Planner算法，也不复制H实验实现。

导航main不修改；主代理独立负责视觉main集成及H研究传播。

空白检查范围：运行改动通过git diff --cached --check；逐字旧控制快照及原样回收相机SDK沿用原有尾随空白，未为格式检查改写原始源文件。
