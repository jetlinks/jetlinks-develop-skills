# 宿主连续性适配与现成后端

本文件只在选择、安装或审计宿主持久化 / hooks 适配时读取。核心 `$task-continuity` 不依赖这里列出的任何产品。

## 先做能力复用

按能力而不是品牌选择：

| 所需能力 | 可复用后端 | 仍由连续性协议负责 |
| --- | --- | --- |
| 生命周期触发、压缩前保存、压缩后注入 | 宿主原生 `PreCompact` / `SessionStart(source=compact)` 或等价事件 | 恢复类型、gate、注入预算、同轮 `first_allowed_action` |
| 会话事件持久化、全文检索、按需取回 | 本地 event store / SQLite / FTS / host memory | Capsule 的当前路线、reference cursor、Source Snapshot、证据有效性 |
| 跨会话语义记忆 | 本地或获准的向量 / knowledge store | 当前任务身份、源码一致性、验收和版本交付 |
| task / issue / thread 增量状态 | cursor / revision / wait / delta API | `ReferencedSources` 的 extracted facts 与重读条件 |

不要因为某插件自称 memory、continuity 或 resume 就把它当成权威状态。用真实前向轨迹验证：压缩后首个动作是否命中 `Next`、是否重读完整历史、是否遗漏约束、源码漂移能否被发现。

## Codex 原生 Hooks

OpenAI 官方 Hooks 已提供 `PreCompact`、`PostCompact`、`SessionStart`、`PreToolUse`、`PostToolUse` 和 `Stop`。根会话压缩后，`SessionStart(source=compact)` 会在紧接着的模型请求前运行，适合作为恢复索引注入点。

- 只用 `PreCompact` 保存或校验有界状态；失败时标记 `SNAPSHOT_REQUIRED`，不要解析不稳定的 transcript 格式来猜完整任务状态。
- 只在 `SessionStart(source=compact)` 注入一次 Capsule、identity match summary 和 `first_allowed_action`；不要再由 `PostCompact` 重复注入。
- 设置严格 `additionalContextLimit`。多个 hooks / plugins 的上下文会累积，不能把完整技能、事件账本和系统图同时塞回模型。
- tool hooks 不是完整安全边界；覆盖不到的工具仍服从语义 gate。

官方文档：[OpenAI Codex Hooks](https://learn.chatgpt.com/docs/hooks)。

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
