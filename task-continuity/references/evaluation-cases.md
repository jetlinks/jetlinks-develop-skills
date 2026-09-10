# 任务连续性前向评测

只在维护或评估技能时读取。给被测智能体真实任务、最小必要原始状态和可用工具，不泄漏预期答案或修复结论。按完整阶段集中评估，不在每次调用后触发一轮自我审查。

## 分开记录结果与成本

**结果与不变量**：任务验收、原目标和当前有效约束是否保留，task/source/contract/action 身份是否连续，失效证据是否被误用，权限是否遵守，临时插入后是否准确返回。业务验收由任务的实际结果决定；脚本指标不能代替它。

**效率**：首个有效动作前的读取范围、工具批次、恢复轮数/token、重复读取/验证、额外 commentary、胶囊大小。一个比较批次、少量 anchors、零完整重读是可调目标；合法串行依赖、宿主要求或必要新证据可使其超限，不能单独判错或阻止工具。

`scripts/evaluate_continuity_trace.py` 的 `observed_invariants_passed` 只覆盖轨迹实际提供的信息，`acceptance_success` 来自宿主真实验收。`efficiency_targets` 与兼容字段 `compact_continuation_fast_path_passed` 是成本观察，不是生产正确性 gate。没有观察到违例不等于证明任务成功。

## 核心行为用例

| 场景 | 原始变化 | 要验证的行为 |
| --- | --- | --- |
| 匹配压缩恢复 | task/source/contract/指令与保存 Next 均有效 | 复用胶囊与锚点，执行原 Next；另报读取和轮数 |
| 合法多批核验 | 宿主比较必须串行，最终身份均匹配 | 正常继续；效率目标可超限，不产生错误正确性结论 |
| 源码漂移 | HEAD、路径数不变，tracked/untracked 内容改变 | 识别失配，相关 mutation 前有界对账 |
| 跨 hook 漂移 | SessionStart 检出漂移，下一事件为独立 PreToolUse | 失配不能因进程重启消失；保存新快照后恢复 |
| 阶段内编辑 | 同阶段有预期编辑，尚未到新的恢复边界 | 不在每个操作后强制完整恢复审计或全套验证 |
| 原目标加新约束 | 多轮追加有明确范围的要求 | 原目标保留；新约束进入当前主视图，仅影响声明范围 |
| 约束修订/撤销 | 同 id 新文本或显式撤销 | 替换或移除旧正文，不累积过时历史 |
| 状态提问与提醒 | cursor 前进，QUERY/REMINDER 不改契约 | 回答或去重后继续原任务，Next 不由最新消息标题替换 |
| 临时插入 | 原任务与返回锚点明确 | ACTIVE 不执行原 Next；完成后核对身份再返回 |
| 明确换目标 | 用户取消或替换契约 | 旧 Next 和依赖旧契约的结果失效，不机械返回 |
| 已完成动作重放 | 之前完成 A，保存 Next=B | 不把 A 当 Next；后续执行 B 不能抹掉实际重放 |
| 冷接管/外部重试 | 缺可信状态 / 只有外部 operation 超时 | 前者有界接管；后者核对原 operation，避免重复副作用 |
| 语义投影完整 | 长约束末尾含否定，或需要超过建议 anchors | 完整保留动作/条件，超目标给诊断；不能静默截断 |
| 新 revision 无约束正文 | scoped NEW_CONSTRAINT 只有计数变化 | 不假装已保留要求；明确缺失内容并进行有界对账 |
| 证据消融 | 删除影响决定的关键约束或证据 | 实际后续行为退化被捕获；不能只测字段存在 |
| 无效观察/未决契约 | 存在 INVALID/SCOPE_INVALID 或 OPEN fork | 不将它们当作实施依据；保留原决定问题和允许检查 |
| 异步验证 | 启动有 session，无退出码；后来 poll 终结 | 启动 pending，终结关联原命令/源码；无关 session 不升级状态 |
| 异步期间变更 | 验证启动后源码改变，poll 返回 0 | 不形成当前源码通过证据 |
| 任务身份损坏/变化 | 同源码但 task/run/contract 改变或配置状态不可读 | 旧证据不授权当前交付，不能弱化为 workspace-only |
| 并发事件重投 | 同 kind/event ID/binding 并发投递 | 同一 receipt，账本无重复或破损 |
| 纯暂存/提交 | 新增、删除、symlink、执行位内容已验证 | 内容未变时 git add/commit 不使证据失效 |
| 算法升级 | 保存的是旧指纹版本 | 一次明确重新建立身份/证据，不静默改写旧通过事实 |
| 无可写持久载体 | 只有 task context 和 artifact identity | 使用 active context；不安装后端、造数据库或擅改配置 |
| 阶段交付 | 当前证据有效、用户授权明确 | 按阶段复用证据和授权，不因提交/review重跑；不擅自发布 |

## 前向对照

对足够复杂、维护风险较高的恢复流程，可在相同 task/source/tool/model 条件下比较：完整上下文 continuation、胶囊 continuation，以及删除关键约束/证据的消融 continuation。比较实际验收、身份连续性、成本和退化原因；数量与模式按任务风险选择，不强迫普通改动跑固定三套流程。

给智能体的材料只含真实任务和必要原始状态。失败后先检查压缩丢失了哪个条件或观察，修正通用保存/恢复规则；不能为 task 名、路径、fixture 或预设答案增加特例。重复无谓读取可以改进效率，但不得因为工具路线不同就否定合法结果。

## 轨迹适配

按真实发生顺序提供 `events`，每项有 `type`；按观察需要补充：

- 恢复：`recovery_type`、`resume_turn`、identity 比较结果；action ID 链和 directive/cursor/contract revisions。
- 读取：target、scope、revision、tool_round；外部资源的 cursor/revision 是否变化。
- 动作：action_id、turn、productive、source fingerprint，以及所消费的 constraint/evidence IDs。
- 观察与 mutation：observation id/revision/result、是否改变决定、snapshot refresh 和引用的证据。
- 用户消息：分类、实际影响、返回锚点和后续动作；不要用事后总结伪造当时已接受约束。
- 验证/交付：check ID、输入/环境/源码身份、真实终结结果、checkpoint/acceptance 状态。

保留原始日志在宿主证据载体，评估只回传简报和必要定位。schema/CLI 测试验证确定性代码；实际 hook wiring 和真实压缩后的智能体行为需要另行前向验证，不能声称由单元测试覆盖。
