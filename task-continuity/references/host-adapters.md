# 宿主连续性适配与现成后端

本文件只在选择、安装或审计宿主持久化 / hooks 适配时读取。核心 `$task-continuity` 不依赖这里列出的任何产品。

## 先做能力复用

按能力而不是品牌选择：

| 所需能力 | 可复用后端 | 仍由连续性协议负责 |
| --- | --- | --- |
| 生命周期触发、压缩前保存、压缩后注入 | 宿主原生 `PreCompact` / `SessionStart(source=compact)` 或等价事件 | 恢复类型、gate、独立 instruction revision 对账、`previous_productive_action_id -> pre_compaction_next_action_id -> post_compaction_first_productive_action_id`、注入预算、同轮 `first_allowed_action` |
| 会话事件持久化、全文检索、按需取回 | 本地 event store / SQLite / FTS / host memory | Capsule 的当前路线、reference cursor、Source Snapshot、证据有效性 |
| 跨会话语义记忆 | 本地或获准的向量 / knowledge store | 当前任务身份、源码一致性、验收和版本交付 |
| task / issue / thread 增量状态 | cursor / revision / wait / delta API | `ReferencedSources` 的 extracted facts 与重读条件 |

不要因为某插件自称 memory、continuity 或 resume 就把它当成权威状态。用真实前向轨迹验证：压缩前后动作 identity 是否连续、压缩后首个动作是否命中 `Next`、是否重读完整历史 / skill / workspace、是否遗漏约束、源码漂移能否被发现。用户改变目标时另行验证 instruction revision 能使旧动作失效。

## Codex 原生 Hooks

OpenAI 官方 Hooks 已提供 `PreCompact`、`PostCompact`、`SessionStart`、`PreToolUse`、`PostToolUse` 和 `Stop`。根会话压缩后，`SessionStart(source=compact)` 会在紧接着的模型请求前运行，适合作为恢复索引注入点。

- 只用 `PreCompact` 保存或校验有界状态；失败时标记 `SNAPSHOT_REQUIRED`，不要解析不稳定的 transcript 格式来猜完整任务状态。
- 只在 `SessionStart(source=compact)` 注入一次 Capsule、identity / instruction match summary、动作 identity 链和 `first_allowed_action`；不要再由 `PostCompact` 重复注入。若动作链不匹配，或首个生产事件重放 previous action，适配器应留下可审计的 route-deviation 事件并保持 `SNAPSHOT_REQUIRED` / `RESUME_AUDIT` 结果，不得用后续正确动作覆盖它。
- 设置严格 `additionalContextLimit`。多个 hooks / plugins 的上下文会累积，不能把完整技能、事件账本和系统图同时塞回模型。
- tool hooks 不是完整安全边界；覆盖不到的工具仍服从语义 gate。

官方文档：[OpenAI Codex Hooks](https://learn.chatgpt.com/docs/hooks)。

### 通用三事件适配契约

宿主可以把原生事件映射为下列最小协议；字段名可适配，语义不能省略：

1. `PreCompact`：在当前边界覆盖写 `Recovery Capsule`、`Continuity Metadata` 和 `Source Snapshot`，记录 `pre_compaction_next_action_id`、`previous_productive_action_id`、`instruction_revision_at_snapshot` 及 `LoadedRules` / 引用 revisions；存在 material semantic fork 时同时保存其 decision question、`OPEN / RESOLVED`、resolution locator、evidence budget、stage admission 和 latest discriminating evidence。若任一视图无法形成一致边界，保存 `SNAPSHOT_REQUIRED`，不要生成猜测性的 Next。
2. `SessionStart(source=compact)`：先独立比较用户指令 revision，再用一个并行批次比较 source / contract / references / rules。匹配时只输出有界 capsule、比较结果和 `first_allowed_action`；投影保留已存在的 fork / evidence budget，但不重新选择契约、重开 Scout 或重新分类阶段。失配时只输出失配 locator、残余身份风险和 `SNAPSHOT_REQUIRED`。不得在该事件中加载完整 skill、完整任务线程、仓库总览或原始日志。
3. `PreToolUse`（若宿主支持）：在匹配恢复切片的首个生产动作前拒绝 full skill reload、unchanged full-history read、workspace-wide scan、`do_not_reopen` 动作和 `previous_productive_action_id` 回放；允许一次保存的 `first_allowed_action`，并把拒绝写入轨迹。对未覆盖的工具路径仍依赖语义 gate 与轨迹评测。

适配器输出应保持有界，优先调用 `scripts/prepare_resume_context.py` 生成投影。把完整事件库留在 reference backend，不把 FTS 命中、原始 transcript 或 hook 调试输出拼进恢复上下文。

### 可选执行收据适配器

仓库提供 `scripts/codex_execution_adapter.py` 作为 Codex 的薄适配层。它不是新的 task store，也不改变核心协议；只有显式配置下列运行态路径时才启用相应能力：

```text
TASK_CONTINUITY_STATE=<portable-state.json>
TASK_CONTINUITY_RECEIPTS=<execution-receipts.jsonl>
TASK_CONTINUITY_WORKSPACE=<source-workspace>
TASK_CONTINUITY_GRAPH_DIRTY=<optional-index-marker.json>
```

运行态应使用宿主、Trellis 或组织已有的不受普通 Git 交付管理的位置。适配器不会修改 `.gitignore`，没有配置时所有 hook 都安全 no-op。若只配置 state，则只执行连续性 mutation gate 与 compact 投影；配置 receipts 时，若同目录已经存在 `continuity.json` 会自动复用但不会创建它，同时执行阶段 / 交付 gate；graph marker 也可单独使用。用 `doctor` 检查实际配置、source fingerprint、账本完整性和当前 gate，不能用“hook 已注册”代替生效验证。

将原生 hook 分别映射到 `pretooluse`、`posttooluse`、`precompact` 和 `sessionstart` 子命令。`PostToolUse` 只对以下高价值事件计算 source fingerprint 并追加 JSONL 收据：

- `apply_patch / Edit / Write` 源码变更，同时只把可选代码索引标记为 dirty；
- 可识别且有确定退出码的 test / lint / typecheck / build 验证；
- Agent dispatch 和 result observation；结果仍必须由主 Agent 显式 `accept-assignment`，spawn 成功不等于集成成功；
- commit、push 和会修改 PR 状态 / 内容的实际工具结果。

阶段结束时用已有的、覆盖当前 source fingerprint 的 passed evidence 执行一次 `checkpoint-stage`。所有验收覆盖、委派结果均由主 Agent 接受后，再执行一次 `complete-task`。门禁语义如下：

| 动作 | 确定性前置条件 |
| --- | --- |
| `apply_patch / Edit / Write` | continuity state 为 `READY`；未配置 state 时不硬拦截 |
| `git commit` | 当前源码存在通过证据和 coherent-stage checkpoint |
| `git push` / `gh pr` 写操作（create、edit、ready、reopen、comment、merge） | 当前源码的最新 checkpoint 有效、所有 dispatch 已接受、whole-task completion 引用有效 acceptance evidence |

源码变化会通过内容指纹使旧证据失效；单纯 stage / commit 不改变内容指纹，因此不会为了交付重复验证。适配器不尝试解析并阻断所有可能写盘的 shell 语句，也不能替代 sandbox、权限控制或语义审查。需要非命令型证据时可用 `record-evidence` 保存有 locator 的 review / inspection / artifact / runtime 结果；这仍须覆盖当前源码且由 checkpoint / completion 显式引用。

代码图更新采用需求驱动协议：源码写入只置 dirty；当 `code-navigation` 已选择该图后端且当前 query envelope 确实需要它时，先运行增量更新，再调用 `graph-refreshed`。不能再把 `code-review-graph update` 或其他整图刷新绑定到每次 Bash、每次编辑、压缩或 session start。

## 可复用第三方后端

### context-mode

[mksglu/context-mode](https://github.com/mksglu/context-mode) 已提供 Codex plugin、`PreCompact` / `SessionStart` hooks、SQLite 会话事件、FTS5 检索和压缩恢复快照。适合复用为本地运行态事件与检索后端，避免自行实现数据库、全文索引、hook installer 和 MCP 检索工具。

使用边界：

- 它的事件快照是 reference backend，不是 `Contract / Checkpoint / DecisionState / Resume`。
- 当前快照按 files / errors / decisions / rules / git / tasks 等事件组织，不提供复合源码指纹、外部 reference cursor、证据 freshness 或稳定 `first_allowed_action`。
- 快照会建议按 FTS 搜索完整细节；当 Capsule 与 source identity 已匹配时，不要为“完整细节”搜索，只有缺失的决策事实才做一次定向检索。
- 它会注入 routing block 并拦截 / 重路由部分工具，安装前必须审查 hook 定义；依赖 Node.js 和本地 SQLite/native dependency，采用 Elastic License 2.0。
- 数据默认保存在本地适配器目录，可用 `CONTEXT_MODE_DIR` 指向明确的非仓库运行态目录。安装、hook trust 和全局工具路由属于显式环境变更，不能静默执行。

### MemPalace

[MemPalace/mempalace](https://github.com/MemPalace/mempalace) 提供 Codex `SessionStart` / `PreCompact` / `Stop` hooks、本地语义检索和跨会话记忆。适合用户明确需要长期语义记忆或跨任务知识检索的场景。

它以 transcript / 内容挖掘和向量检索为主，需要 Python、向量后端和 embedding 模型；不提供确定性的当前 source identity、reference cursor、acceptance evidence 或执行 gate。不要仅为一次任务压缩恢复引入该依赖，也不要让相关性检索覆盖当前任务契约。

### handoff / transcript archive 类插件

Quiver、Rekindle、Codex Continuity 等工具可以生成 handoff、orientation packet 或 transcript 备份。它们适合人工交接和灾难恢复，但 transcript 解析通常不是稳定宿主接口，且“保存了更多历史”不等于“更快命中唯一 Next”。除非真实 continuation 评测证明有增益，否则只作为 fallback locator，不作为默认恢复主视图。

## 安装决策

1. 仅需同一 Codex 会话的压缩续跑：先用原生 compaction + task capsule；缺少自动事件恢复时再考虑 context-mode。
2. 需要跨会话、跨项目语义记忆：评估 MemPalace 或现有组织 memory backend。
3. 只需人工移交：使用现有 handoff artifact，不部署数据库。
4. 已有 Trellis、workflow runtime、task store 或组织 MCP：优先映射其 revision / cursor / checkpoint，不另建平行状态。

任何第三方方案都必须做四项前向验证：hook 真正触发、数据保存在预期位置、匹配恢复不完整重读、source / contract 漂移能阻止旧 `Next`。插件存在、MCP 可连接或快照文本出现都不能单独证明连续性有效。
