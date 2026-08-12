# 上下文压缩与任务恢复规则

本文件用于让长任务在上下文压缩、会话恢复、暂停、交接或模型切换后快速回到正确路线。恢复依赖任务制品与 Git 事实，不依赖模型记忆，也不重新全仓扫描。

## 真相优先级

1. 用户最新指令与已确认任务契约：决定目标、范围、非目标和验收标准。
2. 当前 Git / 工作树事实：决定代码实际处于哪个分支、提交和 diff 状态。
3. 恢复胶囊：决定当前路线、已验证阶段、有效假设、锚点和唯一下一步。
4. 胶囊列出的代码 / 规范锚点：用于恢复必要细节。
5. 其他仓库材料：只有前述事实失配或无法解释当前状态时才定向读取。

恢复胶囊不是新的权威设计，也不能覆盖用户新指令、任务契约或 Git 事实。

## 恢复胶囊

在任务运行态中维护一个有界、可覆盖写的 `Recovery Capsule` 区块。它包含阶段提交后的实际 commit hash，因此必须位于不会进入阶段提交和最终 PR 的 runtime / checkpoint artifact：Trellis 项目优先使用本地 workflow 已定义且经 `git check-ignore -v` 或等价规则确认不受版本控制的 task runtime；若 Trellis 只提供受 Git 管理的 task / `info.md`，保留其中的任务契约，但把胶囊写入一个仓库本地 Git-ignored sidecar。无 Trellis 时写入同一 Git-ignored runtime file。不要用 `assume-unchanged` / `skip-worktree` 隐藏受跟踪文件，也不要为恢复胶囊新增受 Git 管理的 docs。

只保留以下字段：

| 字段 | 内容 |
| --- | --- |
| Task | task ID、revision、任务契约路径 |
| Route | 当前阶段、focused skills、已选解法层级 / 不变量 |
| Validated | 最近完成并验证的阶段、验收信号、对应本地 commit hash |
| In-flight | 尚未提交阶段的当前状态、是否已集中验证、预期 changed paths；没有则写 `none` |
| Worktree | branch、HEAD、预期 changed paths 或 diff-stat 指纹 |
| Live evidence | 仍有效的假设、最新区分证据、禁止重试的已否定路线 |
| Anchors | 恢复下一步所需的 3–7 个精确文件 / symbol / 测试 / 规范路径及读取原因 |
| Next | 一个唯一下一步和它要产生的验收信号 |
| Blockers | 尚需用户 / 外部环境决定的事项；没有则写 `none` |

胶囊应能在约 60 行内表达；字段变化时原位替换。不要写命令流水、全部已完成步骤、长 diff、原始日志、会话总结或重复的设计正文。

## 何时刷新

只在稳定边界刷新，不在每个操作后更新：

- 用户确认或变更任务契约后。
- 根因模型、解法层级或主路线发生变化后。
- 一个连贯阶段完成、集中验证并本地提交后；用实际 commit hash 将该阶段移入 `Validated`。
- 准备暂停、交接、主动压缩长上下文，或判断当前上下文接近需要恢复时。
- 外部事实使 branch / HEAD / changed paths / task revision 指纹失效后。

刷新时压缩旧状态：已完成阶段只保留最近 commit 与验收结论；已否定路线只保留足以阻止重试的一句话。若暂停、交接或压缩发生在阶段提交前，将当前状态写入 `In-flight`，不得预填 commit hash 或把它写入 `Validated`。刷新后再次确认该 runtime path 未进入 `git status --short`；若出现为 tracked / untracked，先修正制品落点，不创建“胶囊更新 commit”。

## 恢复算法

1. **定身份**：读取 active task / task contract 与 Recovery Capsule，确认 task ID、revision、目标和唯一下一步。
2. **对 Git 指纹**：只运行轻量只读检查，例如 `git status --short --branch`、`git diff --stat`、必要时 `git log -n 3 --oneline`；比较 branch、HEAD 和 changed paths。
3. **选择恢复范围**：
   - 指纹匹配：只读取胶囊列出的当前 focused skill / reference 和 3–7 个 anchors，直接继续 `Next`。
   - 指纹部分失配：先查看失配 changed paths、最近提交或 task revision，做有界对账并重写胶囊。
   - task 身份、已确认契约或主分支状态无法建立：停止执行，向用户确认任务归属；不要猜路线。
4. **验证路线仍成立**：用胶囊中的不变量、有效假设和下一验收信号检查新上下文是否沿主线；不因为重新阅读到相邻 TODO 或旧方案而扩大范围。
5. **继续工作**：从唯一 `Next` 开始。不要先重新读取整个 README、全仓目录、所有相邻模块、所有历史文档或已经列为已否定的路线。

## 允许扩大重读的门槛

只有命中以下任一条件，才逐级扩大读取范围：

- 胶囊缺失、字段明显过期或与任务契约冲突。
- Git 指纹表明其他人 / 任务改变了当前代码事实。
- 锚点不存在、公共契约已变化，或当前验收失败无法由胶囊中的假设解释。
- 用户实质改变目标、范围、发布边界或验收标准。

扩大时遵循“失配文件 → 直接生产者 / 消费者 → 所有权边界 → 更广系统图”的顺序；每扩大一级都要说明它要解决的具体失配，不直接回到全仓扫描。

## 偏航门禁

- 恢复后的第一项生产改动必须服务于胶囊的 `Next` 和对应验收信号。
- 若新发现与主任务无关，记录到任务运行态的候选后续项，不顺手实现、不写入权威 docs。
- 若当前代码已超出已确认范围，先定位是哪一阶段 / 提交引入，再决定保留、回退或询问用户；不要用更多改动掩盖偏航。
- 恢复胶囊不能伪造“已验证”；每个 `Validated` 阶段必须能指向测试证据和实际本地提交。集中验证通过但尚未提交的阶段仍属于 `In-flight`。

## 示例骨架

```md
## Recovery Capsule

- Task: `<id>@<revision>`; contract: `<path>`
- Route: `<phase>`; skills: `<skill list>`; invariant: `<one sentence>`
- Validated: `<stage>`; evidence: `<test / signal>`; commit: `<hash>`
- In-flight: `none` / `<stage>`; validation: `<pending / passed>`; expected paths: `<paths>`
- Worktree: branch `<name>`; HEAD `<hash>`; expected paths: `<paths>`
- Live evidence: keep `<hypothesis>` because `<evidence>`; do not retry `<rejected route>`
- Anchors:
  - `<file-or-symbol>` — `<why needed next>`
- Next: `<single action>` → `<observable signal>`
- Blockers: `none` / `<decision needed>`
```
