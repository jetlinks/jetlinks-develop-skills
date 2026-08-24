# Evaluation Cases

Use these cases for forward-testing without showing the Agent the expected route. Compare a full-context single owner, orchestration-enabled run, and an ablation that removes the Assignment Capsule or escalation rule.

## Cases

### Short mechanical change

Request: rename one private symbol with exact references and a deterministic test.

Expected property: `SINGLE_OWNER`; no Agent is spawned merely to satisfy the workflow.

### Independent codebase discovery

Request: map backend and frontend owners for one feature before any edit.

Expected property: at most two `PARALLEL_SCOUTS`, disjoint read scopes, accepted dispatch receipts, terminal results with evidence locators and one parent integration. No complete repository scan and no writes. Merely printing two scout prompts fails the case.

### Advice-only delegation false positive

Request: perform a complex review whose two risk categories are independent and explicitly execute the chosen route.

Expected property: if the current `RouteDecision` selects `PARALLEL_SCOUTS` or `INDEPENDENT_REVIEW` and the host supports it, the trace contains real dispatch, terminal results and integration. A non-`SINGLE_OWNER` route with zero dispatches is invalid. If dispatch is unavailable or unauthorized, revise the route to `SINGLE_OWNER`, record the blocker and execute serially instead of presenting a delegated route as completed.

### Stable disjoint implementation

Request: implement two independent adapters after their shared interface and tests are fixed.

Expected property: parallel workers are allowed only with disjoint write sets; the primary owns the shared interface and integration. Validation occurs after integration, not after every edit.

### Qualifying cross-module program

Request: add a feature whose backend contract, frontend consumer, and integration tests are each substantial, while the API, authorization semantics, and acceptance matrix can be decided before implementation.

Expected property: create one `OrchestrationProgram` with `primary_role: ORCHESTRATOR_INTEGRATOR`. It performs discovery and design / contract-freeze before bounded implementation; each active stage has one current `RouteDecision`. After the primary freezes the cross-slice contract, workers may own mutually exclusive implementation slices, followed by primary integration, conditional independent review, and one coherent-stage validation. Do not introduce frontend- or backend-specific route modes.

### Contract not frozen

Request: implement frontend and backend changes in parallel while the response shape, permissions, or error semantics remain undecided.

Expected property: do not dispatch parallel writers. Keep the contract with the primary and use discovery or `SEQUENTIAL_HANDOFF` until the relevant contract revision is frozen, dependencies are accepted, write sets are disjoint, and acceptance is independently assignable.

### Primary overlaps an active worker

Request: after dispatching a worker for one module, have the primary implement the same files “to speed up” while also coordinating another slice.

Expected property: reject the overlap. The primary accepts results, steers or interrupts stale work, owns shared contracts and resolves integration conflicts, but does not duplicate an active worker's leaf implementation or consume its raw process log as acceptance evidence.

### Stage dependency not satisfied

Request: start a consumer implementation stage before the producer contract or its required artifact is accepted.

Expected property: keep the dependent stage pending or use `SEQUENTIAL_HANDOFF`. Its entry gate requires the accepted dependency and frozen relevant contract; a later stage cannot become active merely because a worker is available.

### Compression recovery without duplicate dispatch

Request: resume a multi-stage program after context compression while one implementation receipt is still active and another result is already collected.

Expected property: reconcile `program_id`, `current_stage`, contract revisions, active assignment IDs, receipts and Result Packets before any dispatch. Do not repeat discovery, spawn a replacement for the active assignment, or spawn again for the collected result; resume from the exact gate that remains unmet.

### Tightly coupled multi-module negative

Request: repair a failure spanning several modules where the common root cause and public contract are still unknown.

Expected property: no implementation program or parallel fix workers. A strong `SINGLE_OWNER` keeps the model and contract decision, optionally using disjoint read-only scouts for discriminating evidence.

### Strong primary, economy mechanical execution, strong acceptance

Request: after a shared interface and deterministic tests are frozen, apply the same reversible adapter change across a large exact file set.

Expected property: an economy executor may own the exclusive mechanical write set, but its success remains `COLLECTED` until the primary checks the actual diff, scope and every acceptance signal. Integration contains only explicitly accepted results.

### Economy write admission rejection

Request: delegate a detailed implementation that still changes authorization, migration, concurrency, lifecycle, a public contract, or an unresolved root cause to the cheapest executor.

Expected property: reject the economy route even when the prompt is detailed. Keep the decision with the strong primary or route a stable ordinary implementation slice to a balanced executor.

### Primary acceptance rejection

Request: an economy worker reports success, but the primary finds an out-of-scope edit or a failed acceptance signal.

Expected property: emit `REJECTED`, preserve the diff and evidence, and repair the capsule, reframe, or escalate. Do not integrate or retry the same economy route with cosmetic prompt changes.

### Unknown shared root cause

Request: several sibling scenarios fail after an initial patch.

Expected property: scouts may collect discriminating evidence, but Agents do not independently add fallbacks. One strong owner reframes the shared invariant before another implementation.

### Cheap worker failure

Request: a low-cost worker returns a failing change, then a slightly different prompt is proposed.

Expected property: classify the failure, preserve evidence and escalate or repair the capsule. Reject a same-tier cosmetic retry.

### Public contract and security boundary

Request: change a persisted schema and authorization behavior.

Expected property: strong primary ownership, serialized writes, explicit user / release decisions and independent review. Cheap scouts may gather authoritative references only.

### Source drift while Agents run

Request: the parent changes a shared input before a worker returns.

Expected property: reject or reconcile the stale Result Packet using its source fingerprint; do not integrate it silently.

### Host without subagents

Request: perform an otherwise parallelizable review where no delegation capability exists.

Expected property: select `SINGLE_OWNER`, record `delegation_blocker: unavailable`, preserve role boundaries serially and produce the same integration / evidence contract without installing an Agent framework.

## Trace checks

Run [`../scripts/evaluate_orchestration_trace.py`](../scripts/evaluate_orchestration_trace.py) against normalized traces. New traces set `schema_version: 2`; schema version 1 remains readable for historical single-stage traces. Include negative traces for:

Each `delegate` event declares `tier: economy | balanced | strong`; an escalation authorizes only a following attempt at the declared higher tier or above.

- missing `RouteDecision` or Assignment Capsule fields;
- non-`SINGLE_OWNER` routing without a real dispatch receipt and terminal result;
- `SINGLE_OWNER` routing that nevertheless emits a delegate event;
- delegation depth greater than the declared limit;
- overlapping writes across active write sets;
- successful results without evidence or source fingerprint;
- economy-tier writes without frozen mechanical scope, deterministic oracle, reversibility, empty risk flags and a primary acceptance owner;
- collected successes without explicit primary acceptance and full acceptance-matrix coverage;
- primary rejection followed by integration or an un-escalated same-tier retry;
- same-slice retry after failure without an escalation event;
- downward or lateral “escalation” that does not increase capability;
- unresolved Agents or delegated work without final integration.

Track task-level acceptance, escaped defects, total calls / tokens when available, time to first productive action, critical-path duration, coordination ratio, duplicate reads, retries, escalations and maximum concurrency. Do not claim improvement from fewer main-thread tokens alone.
