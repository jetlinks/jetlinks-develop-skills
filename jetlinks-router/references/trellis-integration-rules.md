# Trellis 制品集成规则

本文件约束 JetLinks skills 在存在 `.trellis/` 的工作区中如何使用任务制品。Trellis 负责任务生命周期，JetLinks skills 负责领域分析、实现和交付门禁。

## 先发现本地契约

1. 检查 `.trellis/workflow.md`、`.trellis/config.yaml`、`.trellis/.gitignore` 和相关脚本；本地 Trellis 版本与仓库规则优先。
2. 使用项目提供的 current-task 命令识别 active task；没有 active task 时，不猜任务目录、不擅自切换或归档任务。
3. 用 `git ls-files .trellis`、`git check-ignore -v <artifact>` 和本地配置确认跟踪策略。`.trellis` 可能整体忽略、部分强制跟踪或由 finish 流程提交，不能统一假设。

## 职责边界

- Trellis task / PRD：当前任务的目标、范围、非目标、验收标准和待确认方案。
- Trellis task log / implement / check / runtime：当前阶段、执行上下文、步骤、假设、失败与恢复状态；具体文件名以本地 workflow 为准。智能体滚动维护的当前计划与含 commit hash 的 Recovery Capsule 必须放不受 Git 管理的 runtime / checkpoint；若本地同名 artifact 受跟踪，则改用 Git-ignored sidecar。
- Trellis research：区分假设所需的来源、关键事实和调研结论。
- Trellis journal / finish / archive：会话与任务生命周期记录，由 Trellis 流程维护。
- `.trellis/spec/`：稳定、跨任务的项目规范；是否受 Git 管理由本地策略决定。
- 仓库 `docs/` / ADR / API 文档：已接受且当前有效的产品与架构事实，不承担 Trellis 运行态。

focused skill 不主动创建、切换、完成或归档 Trellis task，不写 finish / journal，也不改变 Trellis 的共享 Git 策略，除非用户明确要求或本地 workflow 把该动作定义为当前步骤。若现有 Trellis runtime 全部受 Git 管理，为实时状态选择一个仓库本地 Git-ignored sidecar，不把胶囊更新混入阶段 commit。

## 计划与设计生命周期

1. 待确认设计先更新 active task 的需求 / 设计 artifact；不要同时创建 `docs/plans/...` 草稿。
2. 实时步骤、checkbox、临时下一步、假设账本、失败轨迹和阶段总结进入 Trellis 的运行态 artifact，不进入 PRD 的稳定契约区，更不进入仓库 docs。
3. 计划阶段切换时压缩当前状态：只保留尚未完成的阶段及其验收信号、一个有效工作假设、最新证据、唯一下一步和阻塞；删除 completed checkbox，不把每轮完成项复制成新总结或计数。最近完成阶段由 Recovery Capsule 的 `Validated` 指针承载。
4. 用户确认后，只有长期需求、契约、架构 / API / 模块设计或长期风险发生变化，才原位同步权威 docs。纯任务级实施步骤可以只留在 Trellis。
5. 实现失败且契约未变时，只更新 Trellis 运行态；若证据表明已接受的设计必须改变，先更新 task contract 并重新确认，再同步权威 docs。
6. 完成时由 Trellis 负责 archive / journal；JetLinks delivery 将测试证据写入 PR / CI，只把稳定结论提升到 canonical docs / spec / skill。

## 上下文恢复

遵循 [`context-recovery-rules.md`](context-recovery-rules.md) 维护有界 Recovery Capsule：

- 优先使用本地 workflow 已声明且不受 Git 管理的 runtime / checkpoint artifact；若其定义的 `info.md` 受 Git 管理，只在其中保留任务契约或稳定技术事实，胶囊改用 Git-ignored sidecar。
- 在用户确认契约、路线变化、阶段验证并本地提交、暂停 / 交接 / 压缩前更新；阶段提交后写入实际 commit hash，提交前暂停则只标记 in-flight，不在每个命令后写 journal。
- 恢复时先读 active task、任务契约、胶囊和 Git 指纹，只加载胶囊列出的少量 anchors；不要因对话被压缩就重新扫描全仓。
- 胶囊只保存当前路线索引，不复制 PRD、research、diff 或阶段流水。
- 胶囊刷新后用 `git status --short` 和必要的 `git check-ignore -v` 确认它不会出现在阶段提交或最终 PR 中。

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
