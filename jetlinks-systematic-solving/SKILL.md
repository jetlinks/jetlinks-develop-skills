---
name: jetlinks-systematic-solving
description: 在 JetLinks 复杂、高难度、高不确定性、跨模块或反复失败的开发任务中进行系统性求解。适用于需要跨多个边界理解完整链路、候选根因不唯一、涉及并发 / 生命周期 / 兼容 / 性能 / 权限 / 状态一致性，或已出现同一验收信号修复后仍失败、故障转移到同类场景、不断追加条件分支 / fallback / mock / 兼容层、连续操作没有获得新证据的场景。用于建立可证伪的问题模型、限制局部修补、在停滞时强制重构假设、选择共同根因或显式策略方案，并按原场景、同类场景和反例完成验证；不要用于根因明确且不影响共享契约的单点机械修复。
---

# JetLinks Systematic Solving

Read [`references/systematic-solving-rules.md`](references/systematic-solving-rules.md) before acting. Read [`references/research-basis.md`](references/research-basis.md) only when reviewing or evolving this workflow, or when the user asks for its rationale.

## Workflow

1. Decide the entry mode:
   - Enter proactively for a complex or high-uncertainty task.
   - Enter immediately when a task shows a stagnation signal, even if it started as a small fix.
2. Freeze the task contract before editing: observable success, current failure, invariants, scope, non-goals, constraints, and validation signals. Separate verified facts from assumptions. In Trellis, put the contract in the active task's owning requirement / design artifact and put the live hypothesis ledger in its non-versioned runtime / checkpoint; without Trellis, keep both in one Git-ignored runtime file. Do not append either to authoritative docs.
3. Build the smallest sufficient system map across the real execution path: entry, ownership boundary, data and state transitions, extension points, side effects, and consumers. Inspect all affected variants instead of only the failing sample.
4. Maintain competing, falsifiable hypotheses. For each hypothesis, state the evidence it explains, its prediction, and the cheapest discriminating check. Gather new evidence before choosing a solution level.
5. Classify the solution level:
   - Use a local correction only for a truly local defect under a sound shared contract.
   - Fix the shared abstraction, default implementation, adapter, lifecycle, or contract when sibling scenarios share the cause.
   - Model legitimate differences as explicit policy, strategy, capability, configuration, or business condition.
   - Escalate a real architecture or release-boundary choice to the user before expanding scope or breaking an external contract.
6. Enforce the local-patch budget: allow at most one unverified local implementation attempt under the same root-cause hypothesis. If its acceptance signal still fails, a sibling failure appears, or another special branch would be required, stop editing. Update the bounded runtime state with what the result falsified, rebuild the hypothesis set and system map, then choose again. Replace stale hypotheses and steps instead of accumulating round-by-round summaries. Syntax, import, formatting, and equivalent mechanical corrections within the same coherent implementation are not separate attempts.
7. Implement the smallest **complete** change that restores the invariant for the affected scenario class. Remove obsolete fallback, duplicate compatibility, temporary switches, weakened assertions, and in-PR intermediate forms made unnecessary by the canonical solution.
8. Validate at coherent stage boundaries rather than after every operation. Cover the original trigger, at least one representative sibling when a shared capability changed, a counterexample or boundary, and relevant regressions. If a check fails, compare the failure signature with the previous one before any new edit.
9. At each validated stage boundary, let `$jetlinks-delivery` create one local commit for that coherent stage, then refresh the bounded Recovery Capsule defined by [`../jetlinks-router/references/context-recovery-rules.md`](../jetlinks-router/references/context-recovery-rules.md) with the actual commit hash and next route. If a pause or compaction happens before the commit exists, record the stage as in-flight rather than claiming it is validated. Do not push or create/update a PR yet.
10. Hand domain implementation back to the relevant JetLinks focused skill. Keep this skill responsible for the problem model, stagnation gate, solution level, recovery route, and validation matrix; do not duplicate CRUD, reactive, protocol, web, permission, or delivery rules here.

## Required Constraints

- Optimize for the smallest complete solution, not the smallest diff or quickest green check.
- Do not make a second patch under an unchanged hypothesis merely because the first patch was insufficient.
- Do not let new conditionals, fallback branches, mocks, retries, compatibility aliases, or copied implementations substitute for a revised problem model.
- Do not modify production code until the chosen hypothesis has a falsifiable prediction and supporting evidence.
- Do not repeatedly run the same failing command or inspect the same surface without stating what new information the repetition can produce.
- Do not treat planning as completion. Every plan item must connect to an observable acceptance signal.
- Do not turn the hypothesis ledger, system-map evolution, patch attempts, progress checkboxes, or stage summaries into repository docs. Promote only an accepted stable contract or architectural conclusion, and rewrite its canonical source in place.
- After context compaction or resume, do not reconstruct the whole project by default. Recover from the task contract, Recovery Capsule, Git fingerprint, and its bounded anchors; expand only when those facts conflict.
- Do not over-generalize a local defect. Generalize only to the demonstrated invariant and variation axis, using representative sibling evidence.
- Do not hide uncertainty. When two materially different contracts remain plausible and workspace facts cannot decide, ask one focused question.
- Do not broaden the user-visible scope, break a released or external contract, add a dependency, or introduce a risky workaround without explicit user confirmation.
- Apply [`../jetlinks-conventions/references/root-cause-and-no-hack-rules.md`](../jetlinks-conventions/references/root-cause-and-no-hack-rules.md) for prohibited implementation techniques.

## Response Shape

For analysis or replanning:

1. Task contract and complexity / stagnation trigger
2. Verified facts, assumptions, and current system map
3. Competing hypotheses and discriminating evidence
4. Chosen solution level and rejected local patches
5. Implementation slice and validation matrix
6. User decision needed, if any

For delivery:

1. Root cause and violated invariant
2. Why the solution covers the affected scenario class without over-generalizing
3. Obsolete special handling removed or intentionally retained
4. Original, sibling, boundary, and regression evidence
5. Residual risks and pending external validation
