---
name: task-continuity
description: 压缩长任务计划并在上下文压缩、暂停、恢复或交接后从复合源码指纹、动作身份链、引用 / 规则账本、区分观察和少量锚点继续工作，同时管理运行态分层、阶段验证、证据复用与条件式版本交付。适用于计划开始记流水账、恢复时反复重读任务或项目、压缩后回放上一动作、连续压缩后只分析不执行、最近观察与下一步脱节、脏工作区身份不可靠、实时进度混入权威文档、已有验证证据需要判定有效性，或需要约束“阶段验证后本地 checkpoint、整体完成后统一发布 / review”的场景；先发现宿主实际能力，不要求 Trellis、Git、GitHub、本地文件或生命周期 hooks。
---

# Task Continuity

Read [`references/task-state-and-recovery-rules.md`](references/task-state-and-recovery-rules.md) before acting. When reviewing or evolving this workflow, also read [`references/research-basis.md`](references/research-basis.md) and forward-test [`references/evaluation-cases.md`](references/evaluation-cases.md). Read [`references/host-adapters.md`](references/host-adapters.md) only when selecting, installing, or auditing a host persistence / hook adapter. Do not load these maintenance references for ordinary task recovery.

## Workflow

1. Establish task identity, current revision, observable outcome, scope, non-goals, constraints, and acceptance signals. Treat the user's latest instruction as higher priority than saved state.
2. Discover the active environment's task, checkpoint, workspace-state, source-identity, validation, event / memory index, VCS, lifecycle hook, and review capabilities. Reuse an existing workflow or compatible third-party backend before creating storage, retrieval, or hook infrastructure; do not assume a product, file layout, command, writable artifact, or remote platform.
3. Separate authoritative sources, the task contract, live runtime state, validation evidence, and reusable knowledge by lifecycle. Never select a destination merely by filename or directory name.
4. Maintain the plan as a bounded current-state projection: current phase, active hypothesis or decision, remaining stages and their acceptance signals, one next action, and blockers. Replace stale content; do not append completed steps or round summaries.
5. Maintain a compact model-facing Recovery Capsule with four sections: `Contract`, `Checkpoint`, `DecisionState`, and `Resume`. Give an in-flight slice a stable identity, retain only bounded `do_not_reopen` actions whose replay is likely, and give `Next` an explicit stable `action_id`. Keep source digests, reference / rule revisions, audit counters, `previous_productive_action_id`, `pre_compaction_next_action_id`, the latest user-instruction revision captured with that Next, and full evidence locators in bounded Continuity Metadata beside it. Maintain a separate Source Snapshot for source identity, expected changes, fingerprint strength, and missing layers. These three logical views may share one physical artifact, but machine metadata must not crowd the model-facing recovery index and no view may substitute for another.
6. Gate continuation with `READY`, `SNAPSHOT_REQUIRED`, and `RESUME_AUDIT`. Any observation that changes the active hypothesis, failure signature, observation validity, acceptance state, source identity outside the declared in-flight slice, referenced facts, or unique next action enters `SNAPSHOT_REQUIRED`; refresh bounded state before further solution-changing mutation. When systematic solving has an active observation, keep its compact contract, revision, result, and evidence locator in `DecisionState`; do not impose this schema on simple tasks.
7. Classify recovery as `COMPACT_CONTINUATION`, `COLD_HANDOFF`, or `EXTERNAL_RETRY`. A compact continuation first compares the post-compaction user-instruction revision separately from saved task state. If it changed, refresh the contract and route; otherwise use the saved capsule and at most one bounded parallel identity / revision comparison batch, then on a match perform `RESUME_AUDIT -> READY -> first_allowed_action` in the same resumed turn. The action chain must remain `pre_compaction_next_action_id == first_allowed_action.action_id == post_compaction_first_productive_action_id`; `previous_productive_action_id` is a replay detector, not a fallback Next. A cold handoff may perform one bounded takeover audit to establish missing identity and anchors. An external retry whose task, source, contract, and references did not change keeps the existing `Next` and checks only the uncertain external outcome; it is not a new workspace recovery.
8. When an orchestration capability owns active delegated slices, keep only the `OrchestrationProgram` revision and current stage when present, frozen shared-contract revisions, the current `RouteDecision` revision, assignment IDs and states, source fingerprints, Result Packet locators, integration owner, and critical-path next action in bounded runtime state. On resume, reconcile the program, stage, contract, assignment, and result identities before spawning, waiting, or integrating; do not restart an Agent whose result is active or already recorded.
9. When a host can export the three logical views as JSON, use [`scripts/validate_continuity_state.py`](scripts/validate_continuity_state.py) as the deterministic fast-path gate. The script validates but never mutates runtime or source state. A host adapter may collect observations and apply its suggested gate; the core skill must still work without the script.
10. Validate at coherent stage boundaries rather than after every operation. Map prior evidence to the current acceptance matrix and reuse it when source, inputs, semantics, environment, and freshness remain valid.
11. When the environment provides versioned delivery, keep each validated coherent-stage checkpoint local. Publish once and create or update one task-level review only after the whole task passes; use one draft only when the user explicitly requests intermediate sharing.

## Required Constraints

- Do not put live plans, attempts, discarded hypotheses, logs, Recovery Capsules, test reports, review text, or completion timelines into authoritative product, architecture, API, or repository documentation.
- Do not let the current plan become an audit log. Remove completed checklists, stale alternatives, duplicated summaries, and historical step counts.
- Do not reconstruct an entire workspace merely because conversation context was compressed. Recover from task identity, source fingerprint, bounded state, and exact anchors first.
- Do not treat a third-party memory, transcript archive, event index, or generated resume narrative as authoritative task state. Use it as a reference / evidence backend, recover only missing facts, and keep `Contract / Checkpoint / DecisionState / Resume` plus source identity as the continuation gate.
- Do not enter `READY` with a vague `Next` such as "continue implementation", "continue analysis", or "become familiar with the code". It must identify a bounded mutation, a hypothesis-discriminating check, or a real blocker; name the exact owner / locator or tool action, bound the changed items or read scope, and state the observable signal.
- Do not mutate production state while continuity state is `SNAPSHOT_REQUIRED` or an unresolved `RESUME_AUDIT`. Bounded read-only reconciliation and runtime-state refresh are allowed.
- When `DecisionState` contains an active observation, do not let `PLANNED`, `INVALID`, or `INCONCLUSIVE` authorize a solution mutation. Permit only a bounded observation setup, the single declared observation-repair cycle, a discriminating check, a reframe, or a concrete blocker; `DISCRIMINATING` may authorize the explicitly linked solution mutation.
- Do not treat a base revision plus a dirty-file count as a sufficient fingerprint when uncommitted content exists. Include the strongest available digests for tracked changes, untracked content, nested sources, and expected changed items, or mark the identity as partial.
- A partial fingerprint permits bounded diagnosis. Before production mutation, reconcile task-relevant missing layers or explicitly record the residual identity risk and the exact mutation scope; never present partial identity as a match.
- Do not reread a complete external task, thread, issue, research source, or long reference when its saved revision / cursor is unchanged and the facts needed for the next action are already in the reference ledger.
- For cursor-capable threads or tasks, compare with a non-blocking wait / delta operation first. An unchanged cursor permits no `read_thread` / full-history equivalent; an advanced cursor permits only the new delta, expanding backward only when that delta cannot explain a recorded conflict.
- A matching `COMPACT_CONTINUATION` may spend at most one parallel tool batch on source, contract, reference, and rule identity. It must execute `first_allowed_action` in that resumed turn; commentary that only restates recovery does not satisfy this requirement.
- In a matching `COMPACT_CONTINUATION`, a full skill / rule reload, workspace-wide scan, unchanged full-history read, action listed in `do_not_reopen`, or replay of `previous_productive_action_id` before the saved Next is a route deviation even if the correct action happens later. Do not reconstruct a new Next from the recovery narrative when the saved action identity is still valid.
- Preserve `consecutive_matching_audits` across compaction. Under the default policy, on the second matching audit without intervening new evidence or a productive action, do not reload the full skill set, task history, research, workspace overview, or rebuild the same system map; transition to `READY` and execute `first_allowed_action`. A third analysis-only recovery is an idle loop: perform the exact action, run one discriminating check, or report the concrete blocker.
- Treat the second / third matching-audit thresholds and recommended anchor count as operational defaults to tune with trajectory evidence, not scientific constants. Never weaken the invariant: an unchanged recovery slice must not repeatedly consume turns without new evidence or a productive action.
- Do not claim an in-flight or unverified stage is validated. A validated boundary must point to evidence and the source fingerprint it covers.
- Do not rerun checks merely because work reached commit, delivery, or review. Run only missing, invalidated, failed, or explicitly time-sensitive checks.
- Do not commit after every edit, command, or individual test. A checkpoint represents one coherent, independently accepted stage.
- Do not push or create / update reviews after every stage. Remote review is a completed-task delivery unit unless the user explicitly requests an intermediate share.
- Do not assume Trellis, Git, GitHub, pull requests, local files, a particular agent product, or lifecycle hooks. Treat all as optional adapters.
- Do not make the bundled validators responsible for editing runtime state, source files, VCS state, or remote reviews. They produce diagnostics and metrics; host adapters own collection and authorized mutations.
- Do not silently install a state backend, modify shared ignore rules, start a service, or create a database merely to persist agent state.
- When no safe persistent runtime exists, keep bounded state in the active task context and provide a portable Recovery Capsule before handoff.

## Response Shape

1. Task and source identity
2. Current phase, remaining acceptance stages, and one next action
3. Runtime and authoritative artifact placement
4. Validated boundary, in-flight state, and evidence reuse decisions
5. Recovery anchors and fingerprint status
6. Continuity gate: `READY`, `SNAPSHOT_REQUIRED`, or `RESUME_AUDIT`
7. Local checkpoint versus remote delivery status
8. Blockers or residual risk

## Bundled deterministic tools

- [`scripts/validate_continuity_state.py`](scripts/validate_continuity_state.py): validate one JSON Recovery Capsule / Continuity Metadata / Source Snapshot boundary, compare lightweight observed revisions, enforce optional active-observation action gates, reject vague or inconsistent actions, and recommend `READY`, `RESUME_AUDIT`, or `SNAPSHOT_REQUIRED`.
- [`scripts/evaluate_continuity_trace.py`](scripts/evaluate_continuity_trace.py): evaluate normalized host traces, including pre/post-compaction action identity continuity, recovery-entry replay before the first productive action, time to first productive action, repeated reads or checks, observation integrity, evidence-gated solution changes, snapshot freshness, route deviation, idle recovery, runtime leakage, task-irrelevant graph injection, and full-context / capsule / ablation comparisons.

Both programs accept stdin or a JSON file and use only the Python standard library. A Codex, Trellis, VCS, graph, or other host integration converts native state or events into the portable schema; it must not add host paths or product-specific fields to the core contract.
