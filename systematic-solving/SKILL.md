---
name: systematic-solving
description: 对任意领域中的复杂、高难度、高不确定性、跨边界或反复失败任务进行系统性求解。适用于候选根因不唯一、执行路径跨多个组件、涉及并发 / 生命周期 / 兼容 / 性能 / 权限 / 状态一致性，或已出现一次实现后验收仍失败、故障转移到同类场景、不断追加条件 / fallback / mock / retry / 兼容层、连续操作没有获得新证据的场景；用于建立可证伪的问题模型、限制局部修补、选择共同根因或显式策略方案，并按原场景、同类场景和反例完成验证。不要用于根因明确且不影响共享契约的单点机械修复，也不单独承担计划状态、上下文恢复或版本交付。
---

# Systematic Solving

Read [`references/systematic-solving-rules.md`](references/systematic-solving-rules.md) before acting. When reviewing or evolving this workflow, also read [`references/research-basis.md`](references/research-basis.md) and forward-test [`references/evaluation-cases.md`](references/evaluation-cases.md). Do not load them for ordinary problem solving. When the task also needs long-running state, plan compression, resume, evidence reuse, or versioned delivery, route to an available continuity capability such as `$task-continuity`; do not assume a particular task-state backend or that another skill is installed.

## Workflow

1. Enter proactively for a complex or high-uncertainty task; enter immediately when a small task develops a stagnation signal.
2. Freeze a bounded task contract before implementation: observable outcome, current failure, invariants, variation axes, scope, non-goals, constraints, and acceptance signals. Separate verified facts from assumptions.
3. Build the smallest sufficient system map across the real path: entry, ownership boundary, data and state transitions, extension points, side effects, and consumers. For code tasks whose path is not already bounded, use `$code-navigation` when available. Inspect the variants relevant to the hypothesis, not only the failing sample.
4. Maintain competing, falsifiable hypotheses. For each, state the evidence it explains, its prediction, and the cheapest discriminating check. Gather new evidence before choosing a solution level.
5. Partition observed failures before combining them: production contract defect, stale consumer / oracle, invalid fixture / input, mechanical assembly defect, or unresolved. Put failures in one implementation slice only when evidence shows they violate the same invariant; a stale expectation or invalid fixture is not evidence for another production workaround.
6. Choose the solution level: local correction for a local contract violation; shared abstraction or boundary repair for a shared cause; explicit policy / strategy / capability / configuration for a legitimate variation; user decision for a material scope, architecture, release, or external-contract choice.
7. Allow at most one unverified local implementation attempt under the same root-cause hypothesis. When entering because of stagnation, write the bounded `Attempt` and its falsifiable prediction before the next production behavior change. If its acceptance signal still fails, a sibling fails, or another special branch would be required, stop editing. Replace the attempt with expected result, partitioned actual failure signature, new evidence, falsified assumption, and one next discriminating check; rebuild the bounded hypotheses and system map before choosing again.
8. Implement the smallest complete change that restores the invariant for the demonstrated scenario class. Remove obsolete fallback, duplicate compatibility, temporary switches, weakened assertions, and intermediate forms made unnecessary by the canonical solution.
9. Validate at coherent stage boundaries rather than after every operation. Cover the original trigger, a representative sibling when shared behavior changed, a counterexample or boundary, and relevant regressions. If a check fails, partition and compare its failure signature with the previous one before editing again.

## Required Constraints

- Optimize for the smallest complete solution, not the smallest diff or quickest green check.
- Do not make a second patch under an unchanged hypothesis merely because the first was insufficient.
- Do not let conditionals, fallbacks, mocks, retries, compatibility aliases, hidden switches, or copied implementations substitute for a revised problem model.
- Do not modify production behavior until the chosen hypothesis has a falsifiable prediction and supporting evidence.
- Do not make production code absorb a stale test oracle, obsolete consumer assumption, malformed fixture, or mechanical assembly error. Correct each at its owning boundary and retain evidence for any unresolved item.
- Do not repeatedly run the same failing action or inspect the same surface without stating what new information it can produce.
- Do not rerun the same check with the same relevant source, inputs, environment, and failure signature. First record which hypothesis the rerun can distinguish or which changed input invalidated the earlier result.
- Preserve provenance and uncertainty. Do not use a syntactic, inferred, similarity-based, or runtime-scoped relation as stronger evidence than it provides.
- Do not over-generalize a local defect. Generalize only to the demonstrated invariant and variation axis.
- Ask one focused question when materially different contracts remain plausible and available evidence cannot decide.

## Response Shape

For analysis or replanning:

1. Task contract and complexity / stagnation trigger
2. Verified facts, assumptions, and minimal system map
3. Competing hypotheses and discriminating evidence
4. Failure partitions and shared-invariant grouping
5. Chosen solution level and rejected local patches
6. Implementation slice and validation matrix
7. User decision needed, if any

For delivery:

1. Root cause and violated invariant
2. Why the solution covers the demonstrated scenario class
3. Obsolete special handling removed or intentionally retained
4. Original, sibling, boundary, and regression evidence
5. Residual risks and pending external validation
