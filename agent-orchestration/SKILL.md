---
name: agent-orchestration
description: 在宿主允许委派时，选择单一所有者或有界协作，并完成派发、验收与集成。多文件或工具可用本身不触发多 Agent。
---

# Agent Orchestration

Own delegation and result acceptance, not the domain implementation or diagnostic policy. A skill does not grant delegation or external-action permissions.

## Admission

Keep `SINGLE_OWNER` unless an independent evidence question, exclusively owned implementation slice, or material independent review saves enough quality risk, critical-path time or context to cover coordination cost. Stabilize unresolved shared semantics through [systematic-solving](../systematic-solving/SKILL.md#admission) before parallel implementation. If the host forbids or cannot safely dispatch, remain single-owner.

## Execution

1. Define the slice, acceptance signal, permitted scope and integration owner. Discover only the host capabilities needed for this dispatch.
2. Give each delegate the objective, relevant source / directive / contract identity, read/write scope and required evidence. One writable owner per artifact; dependencies must be accepted before consumption. Leaves do not spawn descendants.
3. Dispatch and collect actual terminal results; a proposed role is not execution. Retain assignment identities across interruptions instead of spawning replacements.
4. Accept only current results whose identity, scope, contract and evidence match the assignment. Reject superseded results; integrate after collection and acceptance. A failed attempt needs informative evidence, a corrected bounded assignment or a stronger owner, not prompt-only retries.
5. New constraints invalidate only affected assignments. Stop dependent work before changing a shared contract. Questions and repeated reminders do not restart dispatch.

For a substantive multi-slice `OrchestrationProgram`, the primary owns contracts, coordination, acceptance and host integration / validation; leaf code, tests, docs and repair stay with workers. An optional read-only scout does not turn ordinary single-owner implementation into a program.

Validate coherent integrated stages and reuse valid evidence. Authority, identity, ownership and required acceptance are gates; counts, verbosity and optional packet fields are efficiency diagnostics.

## Conditional details

- Shared-contract programs, assignment / result schemas, model capability or escalation: read the relevant section of [orchestration rules](references/orchestration-and-routing-rules.md), not the entire reference for a simple dispatch.
- Codex roles or host configuration: [adapter](references/codex-adapter.md).
- Actual resume / handoff: consume existing state or use [task-continuity](../task-continuity/SKILL.md).
- Skill maintenance: [cases](references/evaluation-cases.md), [evaluator](scripts/evaluate_orchestration_trace.py) and [research](references/research-basis.md).

Report the outcome, necessary acceptance evidence and blocker; formal traces are not a normal user-facing deliverable.
