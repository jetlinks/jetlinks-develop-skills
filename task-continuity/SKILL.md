---
name: task-continuity
description: 压缩长任务计划并在上下文压缩、暂停、恢复或交接后从复合源码指纹、引用账本和少量锚点继续工作，同时管理运行态分层、阶段验证、证据复用与条件式版本交付。适用于计划开始记流水账、恢复时反复重读任务或项目、脏工作区身份不可靠、实时进度混入权威文档、已有测试证据需要判定有效性，或需要约束“阶段验证后本地 checkpoint、整体完成后统一发布 / review”的场景；先发现宿主实际能力，不要求 Trellis、Git、GitHub、本地文件或生命周期 hooks。
---

# Task Continuity

Read [`references/task-state-and-recovery-rules.md`](references/task-state-and-recovery-rules.md) before acting. When reviewing or evolving this workflow, also read [`references/research-basis.md`](references/research-basis.md) and forward-test [`references/evaluation-cases.md`](references/evaluation-cases.md). Do not load them for ordinary task recovery.

## Workflow

1. Establish task identity, current revision, observable outcome, scope, non-goals, constraints, and acceptance signals. Treat the user's latest instruction as higher priority than saved state.
2. Discover the active environment's task, checkpoint, workspace-state, source-identity, validation, VCS, and review capabilities. Reuse an existing workflow; do not assume a product, file layout, command, writable artifact, or remote platform.
3. Separate authoritative sources, the task contract, live runtime state, validation evidence, and reusable knowledge by lifecycle. Never select a destination merely by filename or directory name.
4. Maintain the plan as a bounded current-state projection: current phase, active hypothesis or decision, remaining stages and their acceptance signals, one next action, and blockers. Replace stale content; do not append completed steps or round summaries.
5. Maintain a bounded Recovery Capsule with task identity, a source fingerprint that covers in-flight changes, the latest validated boundary, live evidence, an incremental external-reference ledger, 3–7 stable anchors, and one next action. Refresh only at stable boundaries.
6. After compaction, resume, pause, or handoff, enforce a recovery read budget: verify task and source identity, check referenced-source revisions, then load only the capsule, the current rules, and its anchors. Reuse extracted facts when their reference revision is unchanged; expand outward only to explain a recorded mismatch.
7. Validate at coherent stage boundaries rather than after every operation. Map prior evidence to the current acceptance matrix and reuse it when source, inputs, semantics, environment, and freshness remain valid.
8. When the environment provides versioned delivery, keep each validated coherent-stage checkpoint local. Publish once and create or update one task-level review only after the whole task passes; use one draft only when the user explicitly requests intermediate sharing.

## Required Constraints

- Do not put live plans, attempts, discarded hypotheses, logs, Recovery Capsules, test reports, review text, or completion timelines into authoritative product, architecture, API, or repository documentation.
- Do not let the current plan become an audit log. Remove completed checklists, stale alternatives, duplicated summaries, and historical step counts.
- Do not reconstruct an entire workspace merely because conversation context was compressed. Recover from task identity, source fingerprint, bounded state, and exact anchors first.
- Do not treat a base revision plus a dirty-file count as a sufficient fingerprint when uncommitted content exists. Include the strongest available digests for tracked changes, untracked content, nested sources, and expected changed items, or mark the identity as partial.
- Do not reread a complete external task, thread, issue, research source, or long reference when its saved revision / cursor is unchanged and the facts needed for the next action are already in the reference ledger.
- Do not claim an in-flight or unverified stage is validated. A validated boundary must point to evidence and the source fingerprint it covers.
- Do not rerun checks merely because work reached commit, delivery, or review. Run only missing, invalidated, failed, or explicitly time-sensitive checks.
- Do not commit after every edit, command, or individual test. A checkpoint represents one coherent, independently accepted stage.
- Do not push or create / update reviews after every stage. Remote review is a completed-task delivery unit unless the user explicitly requests an intermediate share.
- Do not assume Trellis, Git, GitHub, pull requests, local files, a particular agent product, or lifecycle hooks. Treat all as optional adapters.
- Do not silently install a state backend, modify shared ignore rules, start a service, or create a database merely to persist agent state.
- When no safe persistent runtime exists, keep bounded state in the active task context and provide a portable Recovery Capsule before handoff.

## Response Shape

1. Task and source identity
2. Current phase, remaining acceptance stages, and one next action
3. Runtime and authoritative artifact placement
4. Validated boundary, in-flight state, and evidence reuse decisions
5. Recovery anchors and fingerprint status
6. Local checkpoint versus remote delivery status
7. Blockers or residual risk
