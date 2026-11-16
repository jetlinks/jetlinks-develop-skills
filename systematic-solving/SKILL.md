---
name: systematic-solving
description: 对竞争根因、未决共享契约或无证据反复修补的问题建立可证伪模型。已明确的跨层实现、正常 mock 和已授权 retry 不自动触发。
---

# Systematic Solving

Own causal investigation and unresolved material semantics. Preserve the user's outcome, constraints and authorization; solve the demonstrated class at its owner without inventing a broader abstraction or approval step.

## Admission

Use this skill when materially different causes remain plausible, a shared / high-impact contract is undecided, or diagnostic patches repeatedly fail, move the symptom or add unsupported exceptions.

Layer counts and technology keywords are not admission signals. An already-decided cross-layer change, requested retry policy, test double or mechanical assembly fix proceeds normally. These become stagnation signals only when they mask an unexplained failure or replace the disputed boundary.

## Work from evidence

1. Name the unresolved decision, known facts, affected invariant and acceptance signal. Separate a factual uncertainty from a material product choice.
2. Build the smallest producer–boundary–consumer map. Select a bounded observation that distinguishes candidates; use [code-navigation](../code-navigation/SKILL.md) only if the path is unknown.
3. An observation that misses the boundary or cannot distinguish candidates does not justify a solution-changing patch. Repair the observation, choose a better discriminator or identify the blocker.
4. Stop when evidence decides or one user choice remains. Ask only for that material choice; do not implement dependent contracts while it is open. Continue independent authorized work.
5. Classify failures as production defect, stale consumer / oracle, invalid fixture, mechanical assembly or unresolved cause. Fix the owner and compare results with the prediction before another patch.
6. Make the smallest complete change. Preserve independent trust boundaries and owning state / persistence invariants; do not duplicate guards or add production semantics for tests.
7. Validate at stage boundaries: original trigger, sibling when shared behavior changed, counterexample when boundary risk changed, and affected regressions. Reuse valid evidence.

## Conditional details

- Competing hypotheses, `SemanticFork`, observation states or diagnostic budgets: relevant sections of [solving rules](references/systematic-solving-rules.md). Formal ledgers are unnecessary for ordinary implementation.
- Actual handoff / recovery or useful independent work: [continuity](../task-continuity/SKILL.md) or [orchestration](../agent-orchestration/SKILL.md), only when needed.
- Maintenance: [cases](references/evaluation-cases.md), [evaluator](scripts/evaluate_systematic_trace.py) and [research](references/research-basis.md).

Report the supported cause / decision, changed behavior, evidence and remaining risk. Status questions or repeated reminders do not replace the current objective.
