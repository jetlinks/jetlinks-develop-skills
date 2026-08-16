# Trellis 制品集成规则

本文件约束 JetLinks skills 在存在 `.trellis/` 的工作区中如何使用任务制品。Trellis 负责任务生命周期，JetLinks skills 负责领域分析、实现和交付门禁。

## 先发现本地契约

1. 检查 `.trellis/workflow.md`、`.trellis/config.yaml`、`.trellis/.gitignore`、`.trellis/.version` 和相关脚本；本地 Trellis 版本与仓库规则优先。若项目使用官方 CLI，先查看 `trellis --version` / 项目更新策略，不未经用户授权直接执行会覆盖模板的 `trellis update`。
2. 使用项目提供的 current-task 命令识别 active task；没有 active task 时，不猜任务目录、不擅自切换或归档任务。
3. 用 `git ls-files .trellis`、`git check-ignore -v <artifact>` 和本地配置确认跟踪策略。`.trellis` 可能整体忽略、部分强制跟踪或由 finish 流程提交，不能统一假设。

## 职责边界

- Trellis task / PRD：当前任务的目标、范围、非目标、验收标准和待确认方案。
- Trellis task 的 `prd.md` / `design.md` / `implement.md`：分别承载需求契约、技术设计和有界执行方案；文件是否存在以及命名以本地 workflow 为准。它们可以被审查和归档，但不是逐轮运行态。
- Trellis `.runtime/sessions/` 或本地等价 runtime：官方当前版本用于按 session 隔离 active-task pointer；可以扩展保存 Recovery Capsule、Continuity Metadata 与 Source Snapshot locator，但不要假设 task pointer 本身已经包含复合源码指纹或最新证据。
- Trellis task log / implement / check runtime：当前阶段、执行上下文、步骤、假设、失败与恢复状态；具体文件名以本地 workflow 为准。智能体滚动维护的当前计划、Recovery Capsule、Continuity Metadata 与 Source Snapshot 必须放不受 Git 管理的 runtime / checkpoint；若本地同名 artifact 受跟踪，则改用 Git-ignored sidecar。
- Trellis research：区分假设所需的来源、关键事实和调研结论。
- Trellis workspace journal / finish / archive：官方提供跨会话工作日志与生命周期记录，由 Trellis 流程维护；journal 是审计 / 交接记录，不作为每次恢复的首读状态，也不能替代唯一 `Next`。
- `.trellis/spec/`：稳定、跨任务的项目规范；是否受 Git 管理由本地策略决定。
- 仓库 `docs/` / ADR / API 文档：已接受且当前有效的产品与架构事实，不承担 Trellis 运行态。

focused skill 不主动创建、切换、完成或归档 Trellis task，不写 finish / journal，也不改变 Trellis 的共享 Git 策略，除非用户明确要求或本地 workflow 把该动作定义为当前步骤。若现有 Trellis runtime 全部受 Git 管理，为实时状态选择一个仓库本地 Git-ignored sidecar，不把胶囊更新混入阶段 commit。

## 计划与设计生命周期

1. 待确认设计先更新 active task 的需求 / 设计 artifact；不要同时创建 `docs/plans/...` 草稿。
2. 实时步骤、checkbox、临时下一步、假设账本、失败轨迹和阶段总结进入 Trellis 的运行态 artifact，不进入 PRD 的稳定契约区，更不进入仓库 docs。
3. 计划阶段切换时压缩当前状态：模型主视图只保留 `Contract / Checkpoint / DecisionState / Resume`；删除 completed checkbox，不把每轮完成项复制成新总结或计数。最近完成阶段由 `Checkpoint` 的 validated evidence pointer 承载，详细 digest / revisions / evidence ledger 留在 Continuity Metadata。
4. 用户确认后，只有长期需求、契约、架构 / API / 模块设计或长期风险发生变化，才原位同步权威 docs。纯任务级实施步骤可以只留在 Trellis。
5. 实现失败且契约未变时，只更新 Trellis 运行态；若证据表明已接受的设计必须改变，先更新 task contract 并重新确认，再同步权威 docs。
6. 完成时由 Trellis 负责 archive / journal；JetLinks delivery 将测试证据写入 PR / CI，只把稳定结论提升到 canonical docs / spec / skill。

提升前执行四问门禁：结论是否已确认；离开当前任务后是否仍成立；后续维护者是否需要；已有 canonical 来源是否能原位承载。任一答案为否，就留在 task / runtime / research / PR / CI。`Phase` / `Slice`、fixture / case 编号、当前测试数量、待执行评测、阶段 commit、日期和完成进度永不因“已经验证”而变成权威架构内容。

## 上下文恢复

遵循 [`context-recovery-rules.md`](context-recovery-rules.md) 维护有界 Recovery Capsule：

- 优先使用本地 workflow 已声明且不受 Git 管理的 runtime / checkpoint artifact；若其定义的 `info.md` 受 Git 管理，只在其中保留任务契约或稳定技术事实，胶囊改用 Git-ignored sidecar。
- 在用户确认契约、路线变化、阶段验证并本地提交、暂停 / 交接 / 压缩前更新；阶段提交后写入实际 commit hash，提交前暂停则只标记 in-flight，不在每个命令后写 journal。模型主视图与 machine metadata 可以同文件保存，但恢复时必须能先读主视图、只比较 metadata identity。
- 验证一旦改变 failure signature、acceptance status 或 `Next`，立即将状态置为 `SNAPSHOT_REQUIRED` 并覆盖更新模型主视图、Continuity Metadata 与 Git Source Snapshot；同一已声明切片内不逐命令更新。
- 恢复时先读 active task、任务契约、胶囊主视图和复合 Git 指纹；外部任务 / 会话 / research 先比较 metadata 中的 revision / cursor，未变化时复用已提取事实，只加载少量 anchors；不要因对话被压缩就重新扫描全仓或重读完整历史。
- 胶囊只保存当前路线索引，不复制 PRD、research、diff 或阶段流水。
- 胶囊刷新后用 `git status --short` 和必要的 `git check-ignore -v` 确认它不会出现在阶段提交或最终 PR 中。
- 可选 adapter 可以将 task identity / revision、Git Source Snapshot 和引用 / 规则 revisions 映射为 `$task-continuity/scripts/validate_continuity_state.py` 的通用 JSON，再按 `suggested_gate` 覆盖写 runtime sidecar。核心脚本不理解 `.trellis/` 路径、不修改 task / journal / docs；adapter 也不能把每次校验结果追加成 PRD 或 journal 流水。

## 官方 Trellis 与 Codex Hooks 组合

按官方 Trellis `0.6.14`（官方仓库截至 2026-08-11）的文档与实现，Trellis 已提供：task artifacts（`task.json`、PRD / design / implement、research、context manifests）、按 session 隔离的 active-task runtime、workspace journal、从 `workflow.md` 注入状态 breadcrumb，以及多平台 hook / pull 适配。这些能力适合承载任务身份、契约和 locator，但官方 active-task / session context 默认只提供 Git 状态摘要，不等价于本技能要求的 tracked / untracked / nested 内容指纹，也没有内建 `READY` / `SNAPSHOT_REQUIRED` / `RESUME_AUDIT` 语义。该版本的 Codex `hooks.json` 当前只注册 `UserPromptSubmit` 与 `SubagentStart`；虽然仓库含 `session-start.py`，但没有开箱注册 `PreCompact`、`PostCompact` 或 `SessionStart`，因此下面的压缩恢复门禁属于明确的可选增强，不能写成 Trellis 现成功能。

在支持 OpenAI Codex Hooks 的项目中可以增加可选适配；安装或修改 hooks 前先按官方信任模型审查配置：

- `PreCompact`：覆盖保存 Recovery Capsule、Continuity Metadata 与 Git Source Snapshot；失败时显式保持 `SNAPSHOT_REQUIRED`。
- `PostCompact` 或 `SessionStart(source=compact)`：只注入 `Contract / Checkpoint / DecisionState / Resume`、source / revision match summary、matching-audit count 与必要 locator，并进入 `RESUME_AUDIT`；不要注入完整 metadata ledger、journal、长 diff、完整 rules / system map 或原始日志。
- 上述恢复入口若能执行 adapter，可先生成通用 JSON 并调用确定性状态校验器；只有 `READY` 才注入并授权 `first_allowed_action`，`SNAPSHOT_REQUIRED` 只返回失配 diagnostics / locator。不要把脚本输出当新的长期 task artifact。
- `PostToolUse`：只在观察改变 failure signature / acceptance / source identity / Next 时标记 `SNAPSHOT_REQUIRED`，不为每次只读命令写流水。
- `PreToolUse`：在目标是 `apply_patch` 或可识别的生产写命令且状态不为 `READY` 时阻断；专用 / 托管工具可能绕过本地 hooks，因此技能语义门禁仍是主约束。
- `Stop`：检查唯一 Next、未映射验收项和 capsule freshness，不自动归档任务或制造 commit。

Hook 输出必须有严格大小上限。官方文档说明过大的输出可能溢写到磁盘并降低上下文质量，因此自动化只注入恢复索引与 locator。没有 hooks 的平台继续通过 `$task-continuity` 语义协议和 Trellis 现有 workflow-state / session-start 机制恢复，不降级为完整重读。

官方依据：[`Trellis README / docs`](https://docs.trytrellis.app/zh)、[`Trellis 官方仓库`](https://github.com/mindfold-ai/Trellis)、[`OpenAI Codex Hooks`](https://learn.chatgpt.com/docs/hooks)。

## 避免双写

- 不为同一任务同时维护 Trellis task plan 和 `docs/plans` 实时计划。
- 不把 journal / research / task log 复制成 README、设计稿、PR 或 worklog。
- 不在权威文档追加“本轮实现”“验证通过”“阶段总结”“后续 TODO”；直接更新当前有效结论。
- 不因为 Trellis artifact 被 Git 忽略，就把运行态转存到受 Git 管理的 docs。
- 不因为 Trellis artifact 被 Git 跟踪，就把它误认为长期权威设计；权威性由用途和维护契约决定，不由 Git 状态决定。

## 调度输出

Trellis 场景的 router 分析只需给出：

1. 当前 phase / active task（能确认时）
2. JetLinks focused skills
3. 任务契约与运行态 artifact 归属
4. 是否存在需要用户确认并提升到权威 docs 的稳定设计变化
5. 完成后交还的 Trellis 生命周期步骤
