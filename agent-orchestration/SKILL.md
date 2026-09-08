---
name: agent-orchestration
description: 选择单一所有者或有界委派，并完成派发、验收与集成。适用于独立取证、互斥实现或独立审查有明确收益的任务；短小机械任务、未决共同根因和不可分离的共享写入不自动触发多 Agent。
---

# Agent Orchestration

Use delegation only when it improves the requested outcome, critical path, or context isolation enough to cover coordination cost. Existing user authorization and accepted constraints persist across turns. A skill never adds external-action permissions.

## Admission

Keep `SINGLE_OWNER` when one owner can complete the work directly. Consider a bounded delegate for an independent evidence question, an exclusively owned implementation slice, or a retained artifact with material residual review risk. Multiple files, domains, or available Agent tools are not sufficient reasons to delegate.

For causal uncertainty or unresolved shared semantics, use the [systematic-solving admission rule](../systematic-solving/SKILL.md#admission). Stabilize the decision boundary before parallel implementation. Technical evidence may resolve a factual choice; only the user can decide an unresolved material product preference.

## Execution

1. Preserve the original outcome and accepted user constraints. Identify the current slice, its acceptance signal, permitted scope and integration owner. Discover the host's actual dispatch, collection, isolation and permission capabilities; use serial ownership when safe delegation is unavailable.
2. Declare the smallest useful route. A program is useful only for substantive independently ownable slices. Its primary plans, coordinates, supervises, freezes shared contracts, accepts results and invokes host integration / stage checks. In a delegated program the primary does not implement or repair leaf code, tests, documentation or review findings, including between worker runs; reassign that work to a bounded worker. `SINGLE_OWNER` remains the explicit implementation-owner case.
3. Give each delegate the objective, allowed scope, source / directive identity, required acceptance signals and permissions. Use one writable owner per artifact. Consume only frozen relevant contracts and dependencies already accepted; a producer still running is not an accepted dependency. Ordinary leaves cannot spawn descendants. Start with a flat topology and one or two delegates, adjusting efficiency budgets to real benefit and host limits.
4. When a delegated route is selected and dispatch is safe and authorized, dispatch now, retain the accepted receipt and collect its terminal result. Proposed roles are not execution. A failed attempt needs new evidence, a corrected bounded assignment or a stronger owner; changing prompt wording alone is not progress.
5. Accept results only after checking assignment / task identity when supplied, source, applicable directive and contract revisions, actual scope and evidence for every required signal. Evidence consists of source, artifact, test or observation locators, never agreement booleans. Integrate only current accepted results after collection; an earlier integration cannot cover later results. A changed contract invalidates dependent acceptance and requires fresh work or acceptance against the new revision.
6. Answer a `QUERY` or duplicate `REMINDER` and continue the same mainline; do not redispatch or rewrite contracts for them. A substantive new constraint changes only affected assignments. Stop dependent workers before a shared contract changes, preserve the original goal plus accepted additions, and reject superseded results. Preserve active assignment identities across interruption or compaction instead of spawning replacements.

Validate at coherent boundaries and reuse evidence whose relevant source, inputs, contract and environment still match. Identity, authority, ownership and required acceptance are hard gates. Scout counts, stage naming, verbosity and coordination metrics diagnose efficiency; do not create work or reject an otherwise correct result merely to fill a trace or optional packet field.

## Details only when needed

- For shared-contract programs, economy writes, nested authority or a normalized Capsule / Result Packet, read the relevant section of [orchestration-and-routing-rules.md](references/orchestration-and-routing-rules.md). Ordinary bounded delegation can use the execution rules above without loading the full schema.
- For Codex role/model configuration or host operations, read [codex-adapter.md](references/codex-adapter.md).
- For actual long-running recovery, consume the host's existing continuity state or [task-continuity](../task-continuity/SKILL.md); do not add a state backend for a short dispatch.
- For skill maintenance or trace-adapter validation, use [evaluation-cases.md](references/evaluation-cases.md) and [evaluate_orchestration_trace.py](scripts/evaluate_orchestration_trace.py); consult [research-basis.md](references/research-basis.md) when revising policy. Formal traces are not a required user-facing output.

Report the outcome, material acceptance evidence and remaining blocker. Include route, receipts or coordination details only when they help the user assess the result or when an orchestration audit was requested.
