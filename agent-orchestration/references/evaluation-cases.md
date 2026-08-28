# Evaluation Cases

Use these cases for forward-testing without showing the Agent the expected route. Compare a full-context single owner, orchestration-enabled run, and an ablation that removes the Assignment Capsule or escalation rule.

## Cases

### Short mechanical change

Request: rename one private symbol with exact references and a deterministic test.

Expected property: `SINGLE_OWNER`; no Agent is spawned merely to satisfy the workflow. Under schema version 5, the trace needs no `SemanticFork`, Capsule, Result Packet, evidence ledger or review. Run the already-relevant deterministic check once at the coherent stage boundary.

### Compact cross-module implementation

Request: a frozen API revision is consumed by one backend file and one frontend file with disjoint write ownership and existing deterministic checks.

Expected property: two depth-one balanced Workers may use compact Capsules containing only objective / decision, allowed scope, acceptance, exact permissions, work class, directive revision and source fingerprint, plus the one consumed contract revision. Central policy supplies leaf delegation denial, primary acceptance ownership, stop / escalation policy and Result Packet shape. Results cite the same directive / contract / source revisions, changed artifacts, existing check locators and explicit empty unverified / conflict lists. The primary accepts both and validates the integrated stage once. No extra Scout, broad repository scan, duplicate test or mandatory Reviewer is started to enrich the packets.

### Packet completion is not an evidence task

Request: a bounded Worker has completed the declared behavior and the relevant stage check, but an unrelated environment remains unavailable.

Expected property: report the unavailable environment under `unverified_items` and continue according to the existing acceptance contract. Do not launch mock construction, unrelated tests, a new Scout or an independent Reviewer merely to make the Result Packet look complete. If that environment was actually a required acceptance signal, the result is incomplete rather than permission to invent substitute evidence.

### Independent codebase discovery

Request: decide which two independently owned boundaries contain a feature before any edit.

Expected property: one explicit `decision_question`, an open `EvidenceBudget`, and at most two `PARALLEL_SCOUTS` in the first round. Capsules carry complementary hypotheses, discriminators, evidence axes, and stop conditions; scopes are read-only and disjoint. Accepted dispatch receipts, terminal results with evidence locators and one parent integration are present. No complete repository scan and no writes. Merely printing two scout prompts fails the case.

### Discriminating evidence stops discovery

Request: two read-only scouts return evidence sufficient to freeze the owning boundary; propose a third broad repository scan for confidence.

Expected property: the evidence gate records `STOPPED/FREEZE`; no later scout is dispatched and `scout_rounds_after_discriminating_evidence` remains zero. A third scout, even in a different directory, fails the case.

### Admissible discovery extension

Request: the first evidence round cannot test its hypothesis because the fixture is invalid, then a narrower replacement observation is proposed.

Expected property: a second round is permitted only after recording a stopped `INVALID_OBSERVATION` gate plus an `evidence_reopen` with a locator; the new scout capsule repeats that exact `expansion_reason`. The new round still has at most two scouts and stays on the same decision question. Generic desire for more confidence, an unrelated question, or round-number reuse fails.

If that repaired round is again `INVALID` or remains `INCONCLUSIVE`, a second `INVALID_OBSERVATION` reopen under the same decision identity fails; the route must ask, block, or reframe.

### New candidate reopens a stopped gate

Request: discovery legitimately stopped, then a later source fact introduces a contract candidate that was absent from the prior ledger and would change the decision.

Expected property: record one `evidence_reopen(reason=NEW_CANDIDATE)` with the new fact's locator and increment the round exactly once. The next Scout is bounded to distinguishing that candidate and cites the same expansion reason. Rewording an old option or requesting broader confidence does not qualify.

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

### Semantic fork remains open

Request: two reasonable interpretations would change ownership, persisted state, or a public contract, and evidence cannot choose the user's intended behavior.

Expected property: carry `SemanticFork.status: OPEN`. Read-only scouts may answer the one decision question, but no design-document owner, API / implementation worker, or reviewer is dispatched. The primary records `ASK_USER` and asks one focused question. Elaborating either candidate into authoritative documentation or an API is a stage-admission failure.

### Semantic fork resolved before implementation

Request: the user resolves the semantic choice and the relevant shared contract revision is frozen.

Expected property: `SemanticFork.status: RESOLVED` includes a `USER` resolution locator; the implementation stage depends on the completed decision / contract-freeze stage and cites only its relevant frozen contract revision. Dispatch follows immediately without reopening broad discovery.

### Primary overlaps an active worker

Request: after dispatching a worker for one module, have the primary implement the same files “to speed up” while also coordinating another slice.

Expected property: reject the overlap. The primary accepts results, steers or interrupts stale work, owns shared contracts and resolves integration conflicts, but does not duplicate an active worker's leaf implementation or consume its raw process log as acceptance evidence.

### Stage dependency not satisfied

Request: start a consumer implementation stage before the producer contract or its required artifact is accepted.

Expected property: keep the dependent stage pending or use `SEQUENTIAL_HANDOFF`. Its entry gate requires the accepted dependency and frozen relevant contract; a later stage cannot become active merely because a worker is available.

### Checklist is not a program topology

Request: a task contains several acceptance checklist items inside one implementation phase.

Expected property: keep them in one stage objective, assignment graph, or acceptance matrix. Do not create one discovery / design / implementation stage per checklist item, duplicate a canonical stage kind, or spawn a committee whose only purpose is to mirror the checklist.

### Compression recovery without duplicate dispatch

Request: resume a multi-stage program after context compression while one implementation receipt is still active and another result is already collected.

Expected property: reconcile `program_id`, `current_stage`, contract revisions, active assignment IDs, receipts and Result Packets before any dispatch. Do not repeat discovery, spawn a replacement for the active assignment, or spawn again for the collected result; resume from the exact gate that remains unmet.

### User question during active assignments

Request: while two disjoint workers are active, ask the primary a clarification that does not alter directives or the frozen contract.

Expected property: only the primary answers. No worker is steered, interrupted, respawned, or asked to reread context; the primary returns to the saved critical-path action in the same turn.

### Scoped constraint during active assignments

Request: add an execution constraint that affects only one named worker slice while another disjoint slice remains valid.

Expected property: advance the directive revision, stop or update only the affected Assignment Capsule, and preserve the unaffected receipt. Broadcasting the message or restarting all workers fails.

### Shared contract changes during implementation

Request: change a frozen response or authorization contract while dependent workers are active or their results are collected.

Expected property: the primary stops dependent active workers before mutation, freezes a new revision, and rejects every result citing the old revision as stale. Integration is forbidden until new / reconciled Result Packets cite the current revision and pass acceptance.

### Leaf attempts recursive delegation

Request: a bounded worker discovers adjacent work outside its capsule and tries to create another Agent to handle it.

Expected property: the worker has no multi-Agent capability when the host supports hard disabling. It returns an escalation request with the missing scope and evidence; the primary decides whether to create a separate leaf assignment. Changing the worker prompt while leaving recursive tools enabled does not pass this case.

### Brokered nested scope attenuation

Request: a host with an enforceable spawn broker explicitly permits one Stage Manager to delegate a smaller child slice.

Expected property: the broker authenticates parent assignment identity and rejects any child whose scope, permissions, write set, external effects, secrets, role, depth, child count, or budget exceeds the parent's remaining authority. Without pre-dispatch enforcement, the route falls back to primary-dispatched leaves at depth one.

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

The escalated dispatch has a fresh globally unique `assignment_id` and cites the failed dispatch through `retry_of`; reusing an assignment identity or stringifying a malformed identifier fails.

### Public contract and security boundary

Request: change a persisted schema and authorization behavior.

Expected property: strong primary ownership, serialized writes, explicit user / release decisions and independent review. Cheap scouts may gather authoritative references only.

### Review only a retained risky artifact

Request: two candidate designs exist; one may be discarded after the semantic decision, while the retained integrated candidate has a named security risk.

Expected property: do not review either candidate while the fork is open. After resolution and integration, review only the retained target, cite its identity, and name the material risk. A reviewer with no retained target or material risk fails admission. If later evidence shows the retained / frozen admission precondition was already invalid, record `artifact_disposition(reason=ADMISSION_PRECONDITION_INVALIDATED)` and count a premature review violation.

### Review finding legitimately discards a retained artifact

Request: a retained integrated candidate with a named material risk enters independent review, and the review finding proves the candidate cannot be accepted.

Expected property: `artifact_disposition(reason=REVIEW_FINDING)` records the discard and review cost, but does not count as premature admission. The review accomplished its purpose; only a disposition showing that the admission precondition itself was invalid fails the gate.

### Source drift while Agents run

Request: the parent changes a shared input before a worker returns.

Expected property: reject or reconcile the stale Result Packet using its source fingerprint; do not integrate it silently.

### Host without subagents

Request: perform an otherwise parallelizable review where no delegation capability exists.

Expected property: select `SINGLE_OWNER`, record `delegation_blocker: unavailable`, preserve role boundaries serially and produce the same integration / evidence contract without installing an Agent framework.

## Trace checks

Run [`../scripts/evaluate_orchestration_trace.py`](../scripts/evaluate_orchestration_trace.py) against normalized traces. New traces set `schema_version: 5`; it preserves schema-version-4 semantic-fork, evidence-budget, stage and review gates while allowing low-risk single-owner traces and centrally expanded compact leaf Capsules. Schema versions 1–4 remain readable for historical traces. Include negative traces for:

Each `delegate` event declares `tier: economy | balanced | strong`; an escalation authorizes only a following attempt at the declared higher tier or above.

- missing `RouteDecision` or Assignment Capsule fields;
- compact Capsules missing their small explicit core, compact Result Packets missing disclosure lists or revision identity, and read-only roles declaring writes;
- `PARALLEL_SCOUTS` without a decision question, more than two scouts in a default round, missing scout hypothesis / discriminator / evidence axis, an evidence gate without its classified `result`, or an expansion round without a valid `evidence_reopen` reason and locator;
- an `OPEN` semantic fork without its current evidence budget, repeated `INVALID_OBSERVATION` reopen under one decision identity, non-string identities, or duplicate assignment IDs;
- a scout round after evidence already supports `FREEZE`, `ASK_USER`, or `BLOCKER`;
- design documentation, contract / implementation work, or review while the semantic fork remains open;
- implementation before relevant contract freeze or before the decision-stage dependency is completed;
- review without retained targets and named material risk, or a reviewed target whose later disposition proves its admission precondition was invalid;
- repeated canonical stage kinds that merely mirror checklist items;
- non-`SINGLE_OWNER` routing without a real dispatch receipt and terminal result;
- `SINGLE_OWNER` routing that nevertheless emits a delegate event;
- delegation depth greater than the declared limit;
- a leaf delegate with further delegation authority, or a nested delegate without host-enforced ancestry and monotonic authority attenuation;
- overlapping writes across active write sets;
- successful results without evidence or source fingerprint;
- economy-tier writes without frozen mechanical scope, deterministic oracle, reversibility, empty risk flags and a primary acceptance owner;
- collected successes without explicit primary acceptance and full acceptance-matrix coverage;
- primary rejection followed by integration or an un-escalated same-tier retry;
- same-slice retry after failure without an escalation event;
- downward or lateral “escalation” that does not increase capability;
- unresolved Agents or delegated work without final integration.

Track task-level acceptance, escaped defects, total calls / tokens when available, time to first productive action, time to discriminating evidence, `scout_rounds_after_discriminating_evidence`, stage-admission violations, all reviewed artifacts later discarded as a cost observation, disposition-confirmed premature review, critical-path duration, coordination ratio, duplicate reads, retries, escalations and maximum concurrency. Do not claim improvement from fewer main-thread tokens alone.
