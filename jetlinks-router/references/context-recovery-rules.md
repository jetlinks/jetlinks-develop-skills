# 上下文压缩与任务恢复规则

本文件把通用 [`$task-continuity`](../../task-continuity/SKILL.md) 恢复协议映射到 JetLinks 的 Trellis 与 Git 工作流。恢复依赖任务制品与 Git 事实，不依赖模型记忆，也不重新全仓扫描；其他执行环境使用通用协议自己的 source identity 与 checkpoint 能力。

## 真相优先级

1. 用户最新指令与已确认任务契约：决定目标、范围、非目标和验收标准。
2. 当前 Git / 工作树事实：决定代码实际处于哪个分支、提交和 diff 状态。
3. 恢复胶囊：决定当前路线、已验证阶段、有效假设、锚点和唯一下一步。
4. 胶囊列出的代码 / 规范锚点：用于恢复必要细节。
5. 其他仓库材料：只有前述事实失配或无法解释当前状态时才定向读取。

恢复胶囊不是新的权威设计，也不能覆盖用户新指令、任务契约或 Git 事实。

## 恢复主视图、Continuity Metadata 与 Git Source Snapshot

在任务运行态中维护有界、可覆盖写的语义 `Recovery Capsule`、机器 `Continuity Metadata` 与 Git `Source Snapshot`。它们可以位于同一文件，但必须分别回答“目标与第一动作是什么”“哪些 identity / revisions / evidence 支撑它”“对应哪一份工作树”。它们包含阶段提交后的实际 commit hash，因此必须位于不会进入阶段提交和最终 PR 的 runtime / checkpoint artifact：Trellis 项目优先使用本地 workflow 已定义且经 `git check-ignore -v` 或等价规则确认不受版本控制的 task runtime；若 Trellis 只提供受 Git 管理的 task / `info.md`，保留其中的任务契约，但把运行态写入一个仓库本地 Git-ignored sidecar。无 Trellis 时写入同一 Git-ignored runtime file。不要用 `assume-unchanged` / `skip-worktree` 隐藏受跟踪文件，也不要为恢复胶囊新增受 Git 管理的 docs。

模型主视图只保留以下四个区块：

| 区块 | 内容 |
| --- | --- |
| `Contract` | task ID / revision、契约路径、一句话目标、仍生效的不变量 / 约束和验收信号 |
| `Checkpoint` | 当前 phase、最近 validated stage / evidence / local commit、in-flight 状态和 expected changed paths |
| `DecisionState` | active hypothesis / decision、最新区分证据、足以阻止重试的否定路线，以及后续阶段必须 resurfacing 的关键约束 |
| `Resume` | gate、少量精确 file / symbol / test anchors、执行级 `Next` / `first allowed action`、observable signal、blocker / residual risk |

Continuity Metadata 另行记录 Git Source Snapshot 的 locator / match summary、referenced sources revisions / extracted facts、loaded rules digests / obligations、验证 evidence locator，以及 audit fingerprint / consecutive matching audits / last new evidence。正常匹配恢复只向模型提供 identity / revision match summary，不加载完整账本。

胶囊主视图应能一次完整读取；字段变化时原位替换。不要写命令流水、全部已完成步骤、长 diff、原始日志、会话总结或重复的设计正文。anchors 默认保持 3–7 个只是常用预算，可按真实定位需要收缩或扩展；不得用调整数量为全仓重读开口子。

Git Source Snapshot 单独记录 branch、HEAD / tree、tracked diff digest、untracked manifest digest、相关 submodule / nested source digest、expected changed paths、strength 与 missing layers。Git 工作树有未提交内容时，`branch + HEAD + changed file count` 不是完整指纹。使用当前环境可安全生成的规范化内容摘要：tracked diff digest 覆盖已跟踪变化，untracked manifest digest 覆盖相对路径、类型和内容，submodule / nested digest 覆盖实际参与任务的嵌套源码；同时记录本任务 expected changed paths。无法读取某类内容时将 Source Snapshot 标为 `partial(<missing layers>)`，不写“指纹匹配”。阶段完成并本地提交后优先用 commit / tree 作为稳定 checkpoint，减少长期维护巨型脏树指纹。

发现验证结果改变 active hypothesis、failure signature、验收状态或唯一 `Next`，或发现预期 changed paths 之外的漂移时，立即把 `Resume.gate` 置为 `SNAPSHOT_REQUIRED`。完成主视图、Continuity Metadata 与 Git Source Snapshot 的有界覆盖写前禁止继续生产代码 / 配置修改；同一已声明 in-flight slice 内的 expected path 编辑不按命令逐次刷新。

## 何时刷新

只在稳定边界刷新，不在每个操作后更新：

- 用户确认或变更任务契约后。
- 根因模型、解法层级或主路线发生变化后。
- 验证失败改变失败签名、验收状态或唯一下一步后；不能等到下一次压缩才补。
- 一个连贯阶段完成、集中验证并本地提交后；用实际 commit hash 将该阶段移入 `Checkpoint.Validated`。
- 准备暂停、交接、主动压缩长上下文，或判断当前上下文接近需要恢复时。
- 外部事实使 branch / HEAD / changed paths / task revision 指纹失效后。

刷新时压缩旧状态：已完成阶段只保留最近 commit 与验收结论；已否定路线只保留足以阻止重试的一句话。Recovery Capsule、Continuity Metadata 与 Git Source Snapshot 必须覆盖到同一状态边界。若暂停、交接或压缩发生在阶段提交前，将当前状态写入 `Checkpoint.In-flight`，不得预填 commit hash 或把它写入 `Checkpoint.Validated`。刷新后再次确认该 runtime path 未进入 `git status --short`；若出现为 tracked / untracked，先修正制品落点，不创建“胶囊更新 commit”。

## 恢复算法

1. **进入审计**：压缩、恢复、暂停后继续或交接后先置为 `RESUME_AUDIT`；读取 active task / task contract 与 Recovery Capsule 主视图，确认 task ID、revision、目标、持续约束和执行级唯一下一步。
2. **对 Git 指纹**：只运行轻量只读检查，比较 branch、HEAD、tracked diff digest、untracked manifest digest、相关 nested source 状态和 expected changed paths；干净 checkpoint 可直接比较 commit / tree。不要仅用 `git diff --stat` 或文件数声明匹配。
3. **选择恢复范围**：
   - 指纹匹配：先用机器元数据中的 revision / cursor 对外部引用和 loaded rules 做增量检查；未变化时只返回 match summary 并复用 `extracted facts / obligations`。只读取宿主强制的当前 skill body、`Next` 新需要的 rule 和少量 anchors；若记录了匹配 revision 的 graph flow / edge，直接复用或从该节点做一跳查询。Contract、Checkpoint、DecisionState、Anchors 与 `Next` 一致后显式执行 `RESUME_AUDIT -> READY` 并直接执行 `first allowed action`。
   - 引用变化但 Git 指纹匹配：转 `SNAPSHOT_REQUIRED`，优先读取 cursor 之后的增量或紧凑状态，更新引用账本，不重新读取整个引用任务或扫描源码。
   - 指纹部分失配：转 `SNAPSHOT_REQUIRED`，先查看失配 changed paths、最近提交或 task revision，做有界对账并重写三个逻辑视图。
   - task 身份、已确认契约或主分支状态无法建立：停止执行，向用户确认任务归属；不要猜路线。
4. **验证路线仍成立**：用胶囊中的不变量、有效假设和下一验收信号检查新上下文是否沿主线；不因为重新阅读到相邻 TODO 或旧方案而扩大范围。
5. **继续工作**：从唯一 `Next` 开始。不要先重新读取整个 README、全仓目录、所有相邻模块、所有历史文档或已经列为已否定的路线。

默认恢复读取预算为：用户最新指令、active task / contract、Recovery Capsule 主视图、复合 Git 指纹和引用 / 规则 revision 的比较结果、当前阶段强制规则、少量 anchors。超出预算前必须指出哪个失配需要扩大、要读取的最小范围以及可观察的结束条件。

对 task revision、Git Source Snapshot、引用 revisions、Contract、Checkpoint、DecisionState、Anchors 与执行级 `Next` 计算稳定 audit fingerprint；状态名、次数和时间戳不参与计算。每次指纹匹配且其间没有生产修改、区分检查结果、新证据或真实阻塞时递增连续匹配次数，压缩不能清零：

- 第一次恢复允许执行正常有界审计。
- 默认第二次相同恢复只比较轻量身份，禁止重读完整 router / focused skills / PRD / research、全仓概览或重建同一系统图；匹配后立即执行 `first allowed action`。
- 默认第三次仍只有分析即为空转；只能实施精确 `Next`、运行一个能区分假设的检查，或报告具体阻塞。

第二 / 第三次门槛是由真实 continuation 轨迹调优的适配默认值，不是通用论文常数。调整阈值不能破坏“同一切片不无限分析、无新证据不扩大读取”两个不变量。

用户改变目标，或相关 source / reference / Contract / DecisionState / Next 因新事实改变时，转 `SNAPSHOT_REQUIRED` 并刷新指纹；重复复述、重复读取或上下文压缩不构成新证据。`Next` 只有“继续实现 / 继续分析 / 熟悉代码”时不得转 `READY`，必须先补成 production mutation、discriminating check 或 blocker，并写清精确范围和观察信号。

## 允许扩大重读的门槛

只有命中以下任一条件，才逐级扩大读取范围：

- 胶囊缺失、字段明显过期或与任务契约冲突。
- Git 指纹表明其他人 / 任务改变了当前代码事实。
- 锚点不存在、公共契约已变化，或当前验收失败无法由胶囊中的假设解释。
- 用户实质改变目标、范围、发布边界或验收标准。

扩大时遵循“失配文件 → 直接生产者 / 消费者 → 所有权边界 → 更广系统图”的顺序；每扩大一级都要说明它要解决的具体失配，不直接回到全仓扫描。

## 偏航门禁

- 恢复后的第一项生产改动必须服务于胶囊的 `Next` 和对应验收信号。
- 连续匹配恢复后的第一项允许动作必须等于 `first allowed action`；重新加载相同 skills、PRD、系统图或再次宣布“准备实现”不算进展。
- `SNAPSHOT_REQUIRED` 和尚未完成的 `RESUME_AUDIT` 只允许有界读取、指纹计算和运行态覆盖写，不允许修改生产代码、配置或公共契约。
- 恢复后需要补充调用方或影响面时，从 capsule 的 symbol / flow / edge anchor 扩一跳；不得因为索引工具可用就重新生成或读取整张图。
- 若新发现与主任务无关，记录到任务运行态的候选后续项，不顺手实现、不写入权威 docs。
- 若当前代码已超出已确认范围，先定位是哪一阶段 / 提交引入，再决定保留、回退或询问用户；不要用更多改动掩盖偏航。
- 恢复胶囊不能伪造“已验证”；每个 `Checkpoint.Validated` 阶段必须能指向测试证据和实际本地提交。集中验证通过但尚未提交的阶段仍属于 `Checkpoint.In-flight`。
- 用户禁止提交时，保持 `Checkpoint.In-flight(validation=passed)` 并记录 evidence fingerprint；不得为满足状态机擅自 commit 或伪造 checkpoint。

## 示例骨架

```md
## Recovery Capsule

### Contract
- Task: `<id>@<revision>`; contract: `<path>`
- Objective / invariants / acceptance: `<bounded current contract>`

### Checkpoint
- Phase: `<current phase>`
- Validated: `<stage>`; evidence: `<locator>`; commit: `<hash>`
- In-flight: `none` / `<stage>`; validation: `<pending / passed>`; expected paths: `<paths>`

### DecisionState
- Decision: keep `<hypothesis / policy>` because `<latest discriminating evidence>`
- Persistent constraints: `<constraints that must survive later steps>`
- Do not retry: `<rejected route>`

### Resume
- Gate: `<READY / SNAPSHOT_REQUIRED / RESUME_AUDIT>`; reason: `<transition reason>`
- Anchors:
  - `<file-or-symbol>` — `<why needed next>`
- Next / first allowed action: `<mutation / discriminating check / blocker>`; owner/action: `<exact locator>`; scope: `<changed paths / read boundary>` → `<observable signal>`
- Blocker / residual risk: `none` / `<decision or risk>`

## Continuity Metadata

- Referenced sources: `<locator>@<revision/cursor>`; facts locator: `<metadata key>`
- Loaded rules: `<locator>@<revision/digest>`; obligations locator: `<metadata key>`
- Audit: fingerprint `<digest>`; matching audits `<count>`; last new evidence `<locator / none>`; last productive action `<locator / none>`

## Git Source Snapshot

- Source: branch `<name>`; HEAD / tree `<hash>`; expected paths: `<paths>`
- Fingerprints: tracked `<digest>`; untracked `<digest>`; nested `<digest>`
- Strength: `<strong / partial(missing layers)>`; captured for: `<capsule state / evidence locator>`
```
