# Orchestration and Routing Rules

## Contents

1. Routing objective
2. Orchestration programs
3. Risk and capability routing
4. Collaboration modes
5. Assignment Capsule
6. Execution and write ownership
7. Failure escalation
8. Result integration and verification
9. Cost and trajectory metrics

## 1. Routing objective

Optimize the completed task, not the number of Agents. Delegate only when the expected gain in quality, critical-path time, or context isolation exceeds spawn, duplicated reading, coordination, integration, review, and retry cost.

Choose the route in the task’s natural plan. The following normalized `RouteDecision` is for host integration, handoff or trajectory evaluation; do not require every task to print it:

```text
mode: SINGLE_OWNER | PARALLEL_SCOUTS | BOUNDED_WORKER | INDEPENDENT_REVIEW | SEQUENTIAL_HANDOFF
decision_question: the decision or deliverable this route must produce
uncertainty: low | medium | high
blast_radius: local | bounded | shared | irreversible
coupling: independent | ordered | shared_state
verifiability: deterministic | evidence_backed | judgment_heavy
failure_history: none | one_informative_failure | repeated_or_migrating
benefit: quality | critical_path | context_isolation | none
budget: active_slices, max_depth, read_scope, write_owners, stop_conditions
dispatch: not_applicable | required
delegation_blocker: none | unavailable | unauthorized | unsafe
acceptance_owner: primary integration owner
rationale: concrete comparison with SINGLE_OWNER
```

Use `SINGLE_OWNER` when the rationale is `none`, the work is shorter than a useful handoff, slices are tightly coupled, the same context is required everywhere, or integration risk dominates.

`RouteDecision` describes this task's current execution, not a diagram for later use. Keep a hypothetical topology under `ProposedRoute`. Any non-`SINGLE_OWNER` decision has `dispatch: required`, no blocker, and must advance through `ROUTED -> DISPATCHED -> COLLECTED -> INTEGRATED`. If the host cannot accept a real dispatch, revise the current decision to `SINGLE_OWNER`, preserve the blocker, and execute the bounded roles serially.

For `PARALLEL_SCOUTS`, `decision_question` is an admission gate rather than a label added after dispatch. It must name the one decision the evidence round can change. Do not dispatch a generic “understand the project” scout or several scouts answering unrelated decisions under one route.

Apply control-plane checks progressively. The presence of this skill is not itself a reason to create orchestration artifacts:

| Runtime shape | Required control state |
| --- | --- |
| Low-risk `SINGLE_OWNER`, no shared contract or unresolved semantic fork | A natural next action and relevant stage validation; no Capsule, Result Packet, evidence ledger or reviewer |
| One or two bounded depth-one delegates | Compact Capsule and compact Result Packet; central role policy supplies boilerplate |
| Shared-contract or concurrent writes | Add exact relevant `contract_revisions`, dependency and write-ownership gates |
| Security, authorization, persistence, migration, destructive or irreversible effects | Add the relevant boundary evidence and conditional independent review |
| Unknown root cause or unresolved material semantics | Add the bounded `SemanticFork` / `EvidenceBudget`; do not begin implementation |

The evaluator checks state already produced by execution. It must not cause an Agent to run another search, test or review merely to make a trace more complete. If optional confidence remains missing, preserve it as an unverified item; only a claim required by the current acceptance gate needs supporting evidence.

Separate hard execution gates from quality guidance: scope, authority, contract revision, source identity and required acceptance signals may block a route; response length, presentation style, confidence and optional packet fields must not. A host may observe the latter for offline tuning without dispatching repair work.

## 2. Orchestration programs

An `OrchestrationProgram` is a bounded composition of stages, not a new route mode and not a standing organization. Create one only when all of the following are true:

- the task has at least two substantive slices that can be independently owned after discovery;
- the expected gain in quality, critical path, or context isolation exceeds coordination and integration cost;
- the primary can retain ownership of shared contracts and final integration.

Use `SINGLE_OWNER`, optionally preceded by read-only scouts, when the task is small, tightly coupled, needs the same context everywhere, or has an unknown common root cause. Do not create a program merely because a task names multiple technologies or modules.

```text
program_id: stable identifier for this bounded program
primary_role: ORCHESTRATOR_INTEGRATOR
current_stage: stage_id
stages:
  - stage_id: stable stage identifier, for example discovery or bounded-implementation
    stage_kind: discovery | semantic_decision_contract_freeze | implementation | integration | review | validation
    objective: observable stage result
    depends_on: prior stage_ids whose status is completed
    entry_gate: facts, identities, or contracts required to start
    required_contracts: relevant contract_ids required by this stage
    route_mode: one current RouteDecision.mode
    exit_gate: evidence required to mark the stage complete
    status: pending | active | blocked | completed
shared_contracts:
  - contract_id: stable public or cross-slice contract identifier
    revision: source identity or explicit revision
    state: proposed | frozen | superseded
    owner: primary integration owner
```

The normal stage sequence is `discovery -> semantic_decision_contract_freeze -> implementation -> integration -> review -> validation`. Skip a stage only when its entry and exit gates are already evidenced; `review` is conditional on a retained integration candidate with named residual material risk. A stage may use one of the existing modes, and every active stage has one current `RouteDecision`; the program never replaces that decision. Stage kinds describe purpose, not a mandatory checklist. Repetition or a different order is an efficiency observation; distinct stages with satisfied dependency and contract gates remain valid. Do not create stages or Agents solely to mirror a checklist.

Carry, but do not redefine, the canonical decision states produced by problem solving:

```text
SemanticFork:
  decision_question
  status: NOT_APPLICABLE | OPEN | RESOLVED
  evidence_can_decide
  options
  architectural_consequences
  resolution?: {source: EVIDENCE | USER, decision, locator}

EvidenceBudget:
  round
  scout_count
  status: OPEN | STOPPED
  stop_reason?: FREEZE | ASK_USER | BLOCKER | INVALID_OBSERVATION | SOURCE_DRIFT | HIGH_RISK_GAP
```

Orchestration only consumes these states. When `SemanticFork.status = OPEN`, the admissible delegated work is bounded read-only evidence collection. Do not assign a design-document owner, API or implementation worker, or reviewer. The primary either collects discriminating evidence, asks one focused user question, or records a real blocker. Implementation admission requires `status != OPEN`, completed dependencies, and every `required_contracts` entry at its frozen revision. Integration follows accepted implementation artifacts. Review follows integration only when its admission names retained targets and material risks. Validation runs once on the coherent integrated stage, after conditional review when present.

An `OPEN` material fork always carries its `EvidenceBudget`, including a stopped `ASK_USER` or `BLOCKER` state. Orchestration must not drop that state merely because the current route is `SINGLE_OWNER`; doing so would let compaction or another adapter silently restart discovery.

The `ORCHESTRATOR_INTEGRATOR` owns user-message classification and decisions, the problem model, public and cross-slice contracts, program transitions, dispatch / steer / interrupt decisions, result acceptance, control-plane integration, coherent-stage validation coordination, checkpoints, and delivery. Workers do not reinterpret user messages. A `QUERY` or deduplicated `REMINDER` stays with the primary; a local directive change updates only affected Assignment Capsules; a shared-contract change first stops dependent workers and advances the frozen revision. In a delegated program, the primary is control-plane-only, not a fallback implementer: it must not author or repair production code, tests, documentation, or review findings. A host merge, test invocation, or acceptance decision is control-plane work only; if integration reveals a semantic or source conflict, the primary stops the affected slice and dispatches a fresh bounded assignment. A `SINGLE_OWNER` route remains the explicit exception where the primary is also the implementation owner.

### Primary control-plane boundary

For every delegated `OrchestrationProgram`, classify primary actions as follows:

```text
allowed control-plane actions: design, shared_contract, coordination,
  acceptance, integration, delivery
forbidden delegated-work actions: leaf_implementation, documentation,
  review, direct validation
```

All primary actions in a delegated program have an empty write set. `integration` means applying an already accepted patch or asking the host to merge it; `validation` means dispatching / supervising the stage check and interpreting its result, not editing tests or running an unassigned exploratory test. If a control action needs a non-empty source write set, it is no longer control-plane work: create a new Worker assignment with an exclusive scope and keep the primary as owner of the decision and acceptance.

Before parallel implementation, the relevant shared contracts must be `frozen`, dependencies accepted, active write sets mutually exclusive, and acceptance signals independently assignable. Stage `depends_on` names completed stage IDs. Capsule `depends_on` names completed stage IDs or producer assignment IDs already accepted at dispatch time; an artifact dependency names its accepted producer. Unknown IDs, a running producer or a collected but unaccepted result do not satisfy admission. If any condition is false, use discovery, retain the work under `SINGLE_OWNER`, or serialize the slices with `SEQUENTIAL_HANDOFF`; do not let workers infer a changing contract from each other.

Keep program depth at one and active delegated slices at one or two by default. The primary is the only dispatch owner and delegated roles are leaves. Do not form recursive teams merely because a stage contains multiple domains. After compaction or handoff, reconcile `program_id`, `current_stage`, accepted contract revisions, active assignment IDs and receipts before dispatching; never spawn a replacement for an assignment that is still active or already collected.

Dispatch and result observations should be idempotent when the host supplies a stable event identity. A repeated hook or status delivery must reuse the existing assignment / receipt rather than inflate the program or trigger another validation round. Bind acceptance to the current task, run, workspace and contract revision; a source fingerprint alone is not sufficient to authorize an unrelated task.

## 3. Risk and capability routing

Assess the capability floor before selecting a model or Agent profile.

Use one compact, provider-neutral `CapabilityFloor` only when model choice is material:

```text
judgment: mechanical | bounded_reasoning | architectural
impact: local | shared | irreversible
oracle: deterministic | evidence_backed | judgment
minimum_tier: economy | balanced | strong
```

Derive the minimum tier from the highest active requirement: `mechanical + local + deterministic` may use economy; ordinary implementation judgment or evidence-backed acceptance requires at least balanced; architectural judgment, shared or irreversible impact, or a judgment-only oracle requires strong. Security, authorization, migration, concurrency, lifecycle, external side effects and unknown root cause also set a strong floor. Do not materialize this record for a route where the host has no tier choice or the selection is already fixed by a stronger policy.

| Work shape | Minimum route | Capability guidance |
| --- | --- | --- |
| Exact lookup, bounded scan, formatting, deterministic extraction | `SINGLE_OWNER` or `PARALLEL_SCOUTS` | Cheapest tier that can follow the capsule and cite evidence |
| Read-heavy code mapping with known anchors | `PARALLEL_SCOUTS` | Economical explorer; no edits |
| Large mechanical implementation with frozen contract, deterministic oracle and exact exclusive write set | `BOUNDED_WORKER` | Economy executor is allowed only after the admission gate below |
| Disjoint implementation with stable contract and direct tests but normal code judgment | `BOUNDED_WORKER` | Balanced worker; one write owner |
| Ambiguous requirements, unknown root cause, shared API / schema / migration | `SINGLE_OWNER` plus optional scouts | Strong primary keeps decision and repair ownership |
| Security, permissions, concurrency, destructive or hard-to-reverse change | Strong primary plus `INDEPENDENT_REVIEW` | High-capability, evidence-focused review |
| One failed bounded attempt or moved failure signature | Fresh escalation or reframe | Do not repeat the same economical route |

Do not equate role with model size. A strong model may execute a critical slice; an economical model may plan a trivial deterministic batch. Route on uncertainty, impact and verification cost.

## 4. Collaboration modes

### `SINGLE_OWNER`

Use for short, coupled, sensitive, or judgment-heavy work. The owner may still use deterministic tools and keep intermediate logs out of the user-facing context.

### `PARALLEL_SCOUTS`

Use for independent evidence collection: separate modules, documents, logs, test families, or risk categories. Before dispatch, state one `decision_question` and open an `EvidenceBudget`. The default evidence round starts with one or two scouts with complementary evidence axes; a larger count is an efficiency diagnostic unless an explicit resource limit forbids it. Each scout capsule names one hypothesis, the observation that discriminates it, and the stop condition; its `decision` matches the route question. The parent compares results rather than concatenating them.

At the end of each round, the primary records one evidence gate. `FREEZE`, `ASK_USER`, or `BLOCKER` closes discovery and forbids later scout dispatch unless a later evidenced fact creates a genuinely new candidate or invalidates the former boundary. An additional round is admissible only for a new evidenced candidate, an invalid preceding observation, source-identity drift, or a named high-risk gap; record that exact expansion reason before dispatch. “More confidence”, “complete understanding”, or another broad repository scan is not an expansion reason. Inspect counts above the default two per round for duplicated work; the round number must advance monotonically and stopped evidence gates remain hard admission limits.

Represent the transition to another round with an explicit `evidence_reopen` event rather than overloading `EvidenceBudget.stop_reason`. Its `reason` is one of `NEW_CANDIDATE | INVALID_OBSERVATION | SOURCE_DRIFT | HIGH_RISK_GAP`, it increments the round by exactly one, and it carries the locator that changed the former decision boundary. `INVALID_OBSERVATION` also requires the preceding stopped gate to carry that stop reason. A `NEW_CANDIDATE` may reopen a previously terminal gate only when the locator proves that the candidate was absent from the prior ledger and could change the decision; changing wording or asking for broader confidence is not a new candidate. Every later Scout capsule cites the same reopen reason as `expansion_reason`.

The normalized trace records that decision after all scouts in the round have been accepted:

```json
{
  "type": "evidence_gate",
  "round": 1,
  "status": "STOPPED",
  "stop_reason": "FREEZE",
  "result": "DISCRIMINATING",
  "evidence": ["accepted evidence locator"]
}
```

The top-level `EvidenceBudget` mirrors the final gate. For review admission, declare top-level artifacts as `{artifact_id, status: candidate | retained | discarded}`. A later state change is an `artifact_disposition` event with the artifact identity, new status, evidence locator, and a provider-neutral reason: `REVIEW_FINDING | EXTERNAL_INVALIDATION | ADMISSION_PRECONDITION_INVALIDATED | OWNER_DECISION`. Any later discard remains a cost signal, but it is an admission violation only when the evidence says the retained / frozen admission precondition was already invalid. Discard caused by the review's own finding is successful review behavior, not proof that the review started too early.

### `BOUNDED_WORKER`

Use only after the contract and write set are stable. Assign one coherent implementation slice with named files, symbols, or state ownership. Keep shared contracts and integration with the primary Agent. An economy executor may write only when all of these are true:

- `execution_class` is `mechanical`, `contract_state` is `frozen`, and `oracle` is `deterministic`;
- the write set is exact, exclusive, reversible, and large enough to amortize handoff cost;
- `risk_flags` contains none of `public_contract`, `schema`, `migration`, `authorization`, `concurrency`, `lifecycle`, `external_side_effect`, or `unknown_root_cause`;
- the capsule names a primary `acceptance_owner` and stops at the first informative failure or newly required judgment.

Detailed instructions do not make a judgment-heavy change mechanical. Route ordinary implementation judgment to a balanced executor and retain ambiguous or high-impact decisions with the strong primary.

### `INDEPENDENT_REVIEW`

Use after a material implementation slice is integrated and only when the target remains a retained integration candidate with at least one named residual material risk. The reviewer receives target identities, the contract, diff or artifact, acceptance matrix, and evidence locators—not the intended verdict. It returns findings, confidence and missing evidence, and does not edit unless explicitly reassigned. Do not review a speculative candidate merely because review is present in the generic stage sequence; if a reviewed target is later discarded because its underlying semantic contract was not frozen, the review was admitted too early.

### `SEQUENTIAL_HANDOFF`

Use when later work depends on a verified artifact from an earlier specialty. Transfer a compact Result Packet and source identity. Do not keep both Agents active when only one can make progress.

## 5. Assignment Capsule

Role permissions and ordinary leaf behavior have one central owner. A depth-one delegated slice may send this compact form (`schema_version >= 5`):

```text
profile: compact
objective and decision
allowed_scope
acceptance
permissions: exact read / write scope
work_class
directive_revision
source_fingerprint
```

The normalized record inherits `parent_assignment_id=primary`, the delegate depth, `delegation=denied`, `acceptance_owner=primary`, adjacent-scope exclusion, standard Result Packet fields, stop / escalation policy and a zero-child budget. These are policy defaults, not facts a Worker must research or restate. Use the expanded form only when a field differs or a conditional risk activates it:

- add `contract_revisions` and dependencies only when the slice consumes a shared contract;
- add Scout hypothesis, discriminator, round and evidence axis only for evidence collection;
- add review targets and named material risks only when conditional review is admitted;
- add execution class, contract state, oracle, risk flags and reversibility only for an economy write;
- use the full parent, budget and broker authority fields only for host-enforced nested delegation. A compact capsule is depth-one and cannot request brokered delegation.

The canonical expanded record is:

```text
assignment_id: stable identifier for this slice
parent_assignment_id: primary or the broker-authorized parent assignment
depth: root-relative delegation depth
objective: observable result, not an activity label
decision: decision this result will enable
work_class: evidence_scout | documentation | contract_design | implementation | integration | review | validation
allowed_scope: exact files, symbols, sources, systems, or questions
excluded_scope: adjacent work the Agent must not absorb
inputs: anchors, source fingerprint / revision, verified facts, and relevant constraints
directive_revision: execution constraints / permissions / priority revision for this slice
contract_revisions: exact frozen shared-contract revisions consumed by this slice
acceptance: evidence-backed signals for done
acceptance_owner: primary owner that must accept or reject the terminal result
execution_class: mechanical | bounded_reasoning | judgment
contract_state: frozen | proposed | superseded
oracle: deterministic | evidence_backed | judgment
risk_flags: explicit shared-contract or side-effect risks
reversible: whether the assigned change can be safely reverted
output_contract: Result Packet fields and maximum useful detail
stop_conditions: scope drift, source drift, contradiction, permission need, failed acceptance, or budget exhaustion
escalation_triggers: uncertainty or impact that exceeds the assigned capability floor
permissions: read, write set, external side effects, secrets and approval boundaries
delegation: denied | brokered, with denied required for ordinary leaf roles
```

For `work_class: evidence_scout`, also include:

```text
hypothesis: one falsifiable candidate relevant to RouteDecision.decision_question
discriminator: observation that would distinguish or retire that candidate
scout_round: current EvidenceBudget.round
evidence_axis: complementary source, boundary, or risk dimension owned by this scout
expansion_reason: omitted in round one; one of NEW_CANDIDATE | INVALID_OBSERVATION | SOURCE_DRIFT | HIGH_RISK_GAP later
```

For `work_class: review`, also include `review_targets` and non-empty `material_risks`. Targets must be marked retained at admission. A later discard records its disposition reason: `ADMISSION_PRECONDITION_INVALIDATED` proves the review started before its target was stable, while `REVIEW_FINDING` proves the review itself supplied the discard decision and must not be counted as premature admission.

An activity such as “inspect the code” is not an objective. Prefer “identify the owner and all direct consumers of symbol X at source fingerprint Y, cite exact locators, and flag unresolved dynamic edges.”

Capsule authority is monotonic. A child capsule must satisfy:

```text
allowed_scope(child)       ⊆ allowed_scope(parent)
permissions(child)         ⊆ permissions(parent)
write_set(child)           ⊆ write_set(parent)
external_effects(child)    ⊆ external_effects(parent)
secrets(child)             ⊆ secrets(parent)
budget(child)              ≤ remaining_budget(parent)
depth(child)               = depth(parent) + 1
```

The child cannot add public-contract ownership, final acceptance, delivery, commit, push, PR, approval, or external-side-effect authority that the parent did not receive. Missing authority produces an escalation request to the parent; it never justifies self-expansion.

## 6. Execution and write ownership

- A complete capsule plus an accepted host dispatch response marks `DISPATCHED`. Text that recommends, simulates, or drafts a spawn request does not. Retain a compact opaque `dispatch_receipt`; do not place provider-specific thread fields in the core contract. Every dispatch has a globally unique native non-empty `assignment_id`; adapters must not stringify `null`, objects, or arrays into identities. A fresh escalated attempt receives a new assignment identity and cites the failed identity in `retry_of`, so concurrent or historical state cannot be overwritten.
- The normalized `delegate.write_set` must exactly match `capsule.permissions.write`; active write sets must remain disjoint.
- Once a delegated route is selected and dispatch is safe and authorized, invoke the host operation immediately. Do not return a routing report first and wait for the user to repeat the delegation request.
- Collect one terminal Result Packet for every accepted receipt before integration. Hosts may expose explicit wait / join operations or deliver terminal results automatically; the core contract requires the result, not a particular API name.
- Treat `result.status: success` as `COLLECTED`, not accepted. The capsule's primary acceptance owner must emit `ACCEPTED` or `REJECTED` after checking source identity, actual artifacts or diff, exact write scope, and a complete acceptance matrix. Only accepted results may enter integration.
- A normalized acceptance event uses this provider-neutral shape; evidence values are locators, not Agent agreement:

```json
{
  "type": "accept",
  "assignment_id": "stable-slice-id",
  "owner": "primary",
  "status": "accepted",
  "scope_checked": true,
  "artifacts_checked": true,
  "source_fingerprint": "source-revision",
  "acceptance_matrix": {
    "declared signal": ["evidence locator"]
  }
}
```

`artifacts_checked` is mandatory for a non-empty write set. `REJECTED` is an informative failure and must preserve the violated signal and evidence before capsule repair, reframing, or capability escalation.
- Default delegation depth: one. The primary is the only dispatch owner; ordinary children have `delegation: denied` and their Agent tools are hard-disabled when the host supports it. A child requests adjacent help through its Result Packet; the primary decides whether to create a separate leaf assignment.
- Depth greater than one is valid only when the host has an enforceable spawn broker or equivalent pre-dispatch policy. It must authenticate assignment ancestry, permit only declared child roles, intersect the requested capsule with the parent's remaining authority, enforce depth / child-count / token limits, and reject the spawn before side effects when any authority expands. If this capability is absent, prompt instructions and after-the-fact diff review do not make nested delegation safe; retain `max_depth = 1`.
- Default active delegated slices: one or two. Increase when independent critical-path work remains after integration cost is considered; the default is diagnostic, while an explicit host or user concurrency cap is a hard limit.
- Assign a single owner to each file, public contract, schema, migration, runtime resource, and external side effect.
- Parallelize read-only discovery only within the admitted evidence round. Scopes, evidence axes, hypotheses and discriminators must be complementary; the shared decision question remains identical. Serialize overlapping writes and dependent checks.
- Keep the primary context to contracts, decisions, evidence indexes, conflicts and integrated outputs. Store or cite raw logs at their source.
- Keep the primary out of delegated production work: no leaf implementation, test or documentation authoring, review fixing, or direct validation edits. A primary action with a non-empty write set is a control-boundary violation whenever the current route is a delegated program.
- In an active program, only start a stage after its semantic, contract, `entry_gate`, and dependency admission conditions hold. Complete it only when its `exit_gate` has evidence; update `current_stage` rather than appending operational history. A checklist item does not justify another stage kind or another Agent by itself.
- Interrupt or stop work whose inputs have become stale; do not let an obsolete Agent finish merely because it already consumed tokens.
- When a continuity capability exists, persist only the `RouteDecision` revision, active assignment IDs and status, source fingerprints, Result Packet locators, integration owner and exact critical-path next action. After compaction or handoff, reconcile those identities before spawning; do not duplicate an Agent whose result is still running or already recorded.

### Conditional normalized revision events

These fields are for maintained audit traces and host adapters, not a ledger required for every user message. Schema 5 remains current; historical schema 1–4 traces remain readable.

- If the trace declares `task_id`, `run_id` or `workspace_id`, every `delegate`, `result`, `accept` and `integrate` event must carry exactly that identity. Without these optional bindings a historical trace does not itself prove cross-task authority; the live host must bind its task and workspace. Capsule source identity, when present, must match the result, and acceptance must match the collected result identity.
- An optional top-level `directive_revision` is the current revision for new dispatch. A `directive_update` event has `owner: primary`, a new `directive_revision`, `affected_assignment_ids`, `stopped_assignment_ids` and evidence locators. Stop affected active assignments before continuing, invalidate affected collected / accepted / integrated results, and dispatch a fresh assignment at the new revision. Unaffected assignments keep their valid original receipt and directive. Do not broadcast a local change.
- `contract_update` advances the named frozen contract revisions, stops dependent active assignments and invalidates dependent collected / accepted / integrated results. Schema 5 requires fresh current-revision results to cover the changed obligations before final completion. Historical schema 1–4 can opt into explicit coverage with the same conditional replacement / cancellation fields; an older trace without those links does not establish complete replacement coverage. A reassignment conditionally declares `delegate.supersedes` as one invalidated assignment ID or a non-empty list of IDs; only its current acceptance resolves those obligations. Matching files or acceptance labels does not infer replacement. The update may explicitly declare `cancelled_assignment_ids` when the accepted change removes those obligations; its owner, evidence and affected-worker stops still apply. Do not revive already retired assignments on a later revision update.
- An optional `user_message` observation with `message_class: QUERY | REMINDER` is passive: it does not change the saved Next, directives, contracts or assignments. A message that actually changes accepted obligations instead needs the scoped directive or contract transition. No passive event is required for each ordinary query.
- Required evidence and acceptance-matrix values are a non-empty locator string or a non-empty list of non-empty locator strings. Boolean agreement, numbers, objects and empty strings do not prove an acceptance signal.
- `integrate` occurs after terminal collection of all active receipts and current acceptance. Its optional `assignment_ids` selects current accepted results; when omitted it includes all currently accepted results. Every accepted result must be covered by a subsequent integration. Intermediate subset integration is valid while other invalidated obligations remain pending, but a completed trace must resolve each by accepted explicit replacement or authorized cancellation. An earlier integration cannot retroactively cover later dispatch, collection or acceptance.

## 7. Failure escalation

Classify a failed result before another spawn:

- `CAPABILITY_MISMATCH`: the slice required reasoning, tools or context beyond the assigned tier.
- `CAPSULE_DEFECT`: objective, scope, inputs or acceptance were ambiguous or contradictory.
- `SOURCE_DRIFT`: the task-relevant source identity changed.
- `INVALID_OBSERVATION`: the tool, fixture, environment or oracle could not test the prediction.
- `CONTRACT_DEFECT`: the shared problem model or acceptance contract was wrong.
- `IMPLEMENTATION_DEFECT`: the stable capsule was understood but the bounded change failed.

After one informative failure, choose exactly one of: repair the capsule, repair one invalid observation, reframe the shared problem, or escalate to a stronger fresh owner. Do not send the same slice to the same capability tier with cosmetic prompt changes.

The default is one concentrated observation-apparatus repair. Repeated `INVALID_OBSERVATION` reopening is an efficiency warning: inspect whether another observation has new discriminating value. If it does not, change the observation, ask a focused question or report a blocker; changing decision identity does not erase an unchanged failure.

An escalation's `from_tier` must match the tier of the failed or rejected attempt; `to_tier` must be strictly stronger. Do not manufacture an apparent escalation by misreporting the failed tier.

A primary acceptance rejection is an informative failure. Preserve the rejected diff, violated scope or signal, and evidence; then repair the capsule, reframe under the primary owner, or escalate. A worker's self-reported success does not authorize another same-tier attempt.

The escalation packet contains verified facts, unchanged constraints, source fingerprint, artifacts or diff, exact failure signature, invalidated assumptions, evidence locators and the decision still needed. Exclude unsupported speculation and the previous Agent's hidden reasoning chain.

## 8. Result integration and verification

Return only the delegated result and relevant acceptance evidence in ordinary interaction. When a host requires a normalized compact `Result Packet`, use this form; empty `unverified_items` and conflict lists are valid and require no additional investigation:

```text
assignment_id, status and directive_revision
relevant contract_revisions only when consumed
changed_artifacts; empty for a read-only role
source_fingerprint and evidence locators already produced by execution
unverified_items
scope_or_contract_conflicts
escalation request only when needed
```

Do not launch a new check just to replace an honest empty or unverified field with a stronger-looking packet. Evidence locators may point to existing tests, diffs, source anchors or runtime observations; do not copy raw logs into the packet. For a write result, `changed_artifacts` must be non-empty and inspected before acceptance. `evidence_scout`, `review` and `validation` are read-only work classes and must not return changed artifacts.

The primary Agent must:

1. Match assignment, source identity, allowed scope and write ownership.
2. Separate facts from inference and compare conflicting results.
3. Map evidence to the parent acceptance matrix; do not count Agent agreement as independent evidence.
4. Emit one explicit acceptance decision whose matrix covers every declared signal; for write slices also confirm artifacts or diff and scope were inspected.
5. Reject rather than integrate stale, out-of-scope, contradictory, or incompletely evidenced work.
   A Result Packet is stale when any consumed contract revision or affected directive revision differs from the current required revision, even if its source diff and tests otherwise look valid. Preserve the original objective, accepted constraints and existing authorization across turns; a query or reminder does not replace them.
6. Inspect shared-contract effects and perform only control-plane integration under one owner; reassign semantic conflicts instead of editing a Worker slice.
7. Add an independent review only for named residual material risk on an artifact that will be retained.
8. Coordinate one coherent integrated-stage validation, reusing still-valid prior evidence; do not create a primary-side test implementation to fill a gap.

## 9. Cost and trajectory metrics

Measure outcomes per task class; do not optimize a single trace.

- Cost: primary and delegated calls, available token / monetary usage, duplicated-read ratio, failed-attempt cost.
- Efficiency: time to first productive action, critical-path duration, idle wait, integration time, coordination-to-work ratio.
- Quality: acceptance pass rate, escaped defects, evidence completeness, reviewer yield, rework after integration.
- Routing: delegation rate, non-delegation accuracy, escalation rate, weak-retry count, maximum concurrency and depth.
- Discovery admission: scouts per round, time to first discriminating evidence, `scout_rounds_after_discriminating_evidence`, expansion reasons, and evidence-budget stops.
- Stage admission: unresolved-semantic-fork design / implementation / review attempts, implementation before relevant contract freeze, all later-discarded reviewed artifacts as cost observations, disposition-confirmed premature review admissions, and unnecessary stage count.
- Cascading: economy-write admission rate, primary rejection rate, post-acceptance rework, cost per accepted slice and stronger-tier escalation rate.
- Stability: source-drift stops, overlapping-write incidents, capsule defects, unresolved Result Packets.
- Control overhead: compact versus expanded capsules, checks started only to populate control records, repeated still-fresh validation, and coordination-to-accepted-work ratio.
- Role separation: primary work-boundary violations, primary source-write attempts during delegated programs, reassigned integration conflicts, and direct validation / review work incorrectly retained by the primary.

Compare `SINGLE_OWNER` against the proposed route on representative tasks. A multi-Agent route is not an improvement when it only moves tokens to hidden threads or improves one benchmark while increasing rework and escaped defects.
