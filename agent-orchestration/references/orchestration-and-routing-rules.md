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

Record one bounded `RouteDecision`:

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
    objective: observable stage result
    depends_on: prior stage_ids or explicit accepted artifacts
    entry_gate: facts, identities, or contracts required to start
    route_mode: one current RouteDecision.mode
    exit_gate: evidence required to mark the stage complete
    status: pending | active | blocked | completed
shared_contracts:
  - contract_id: stable public or cross-slice contract identifier
    revision: source identity or explicit revision
    state: proposed | frozen | superseded
    owner: primary integration owner
```

The normal stage sequence is `discovery -> design-contract-freeze -> bounded-implementation -> integration -> independent-review -> stage-validation`. Skip a stage only when its entry and exit gates are already evidenced; `independent-review` is conditional on residual material risk. A stage may use one of the existing modes, and every active stage has one current `RouteDecision`; the program never replaces that decision.

The `ORCHESTRATOR_INTEGRATOR` owns user decisions, the problem model, public and cross-slice contracts, program transitions, dispatch / steer / interrupt decisions, result acceptance, integration, coherent-stage validation, checkpoints, and delivery. While a worker is active, the primary does not enter a competing leaf-implementation action, concurrently write the worker's owned scope, or absorb raw process logs. It may still change its own shared-contract or integration-conflict scope when doing so invalidates or stops affected work first, and may implement bounded work before dispatch or after active workers have returned.

Before parallel implementation, the relevant shared contracts must be `frozen`, all `depends_on` artifacts accepted, active write sets mutually exclusive, and acceptance signals independently assignable. If any condition is false, use discovery, retain the work under `SINGLE_OWNER`, or serialize the slices with `SEQUENTIAL_HANDOFF`; do not let workers infer a changing contract from each other.

Keep program depth at one and active delegated slices at one or two by default. The primary is the only dispatch owner and delegated roles are leaves. Do not form recursive teams merely because a stage contains multiple domains. After compaction or handoff, reconcile `program_id`, `current_stage`, accepted contract revisions, active assignment IDs and receipts before dispatching; never spawn a replacement for an assignment that is still active or already collected.

## 3. Risk and capability routing

Assess the capability floor before selecting a model or Agent profile.

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

Use for independent evidence collection: separate modules, documents, logs, test families, or risk categories. Give each scout a disjoint question or scope. The parent compares results rather than concatenating them.

### `BOUNDED_WORKER`

Use only after the contract and write set are stable. Assign one coherent implementation slice with named files, symbols, or state ownership. Keep shared contracts and integration with the primary Agent. An economy executor may write only when all of these are true:

- `execution_class` is `mechanical`, `contract_state` is `frozen`, and `oracle` is `deterministic`;
- the write set is exact, exclusive, reversible, and large enough to amortize handoff cost;
- `risk_flags` contains none of `public_contract`, `schema`, `migration`, `authorization`, `concurrency`, `lifecycle`, `external_side_effect`, or `unknown_root_cause`;
- the capsule names a primary `acceptance_owner` and stops at the first informative failure or newly required judgment.

Detailed instructions do not make a judgment-heavy change mechanical. Route ordinary implementation judgment to a balanced executor and retain ambiguous or high-impact decisions with the strong primary.

### `INDEPENDENT_REVIEW`

Use after a material implementation slice is integrated. The reviewer receives the contract, diff or artifact, acceptance matrix, and evidence locators—not the intended verdict. It returns findings, confidence and missing evidence, and does not edit unless explicitly reassigned.

### `SEQUENTIAL_HANDOFF`

Use when later work depends on a verified artifact from an earlier specialty. Transfer a compact Result Packet and source identity. Do not keep both Agents active when only one can make progress.

## 5. Assignment Capsule

Every delegation must contain:

```text
assignment_id: stable identifier for this slice
parent_assignment_id: primary or the broker-authorized parent assignment
depth: root-relative delegation depth
objective: observable result, not an activity label
decision: decision this result will enable
allowed_scope: exact files, symbols, sources, systems, or questions
excluded_scope: adjacent work the Agent must not absorb
inputs: anchors, source fingerprint / revision, verified facts, and relevant constraints
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

- A complete capsule plus an accepted host dispatch response marks `DISPATCHED`. Text that recommends, simulates, or drafts a spawn request does not. Retain a compact opaque `dispatch_receipt`; do not place provider-specific thread fields in the core contract.
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
- Default active delegated slices: one or two. Increase only when independent critical-path work remains after integration cost is considered.
- Assign a single owner to each file, public contract, schema, migration, runtime resource, and external side effect.
- Parallelize read-only discovery freely only when scopes and questions are disjoint. Serialize overlapping writes and dependent checks.
- Keep the primary context to contracts, decisions, evidence indexes, conflicts and integrated outputs. Store or cite raw logs at their source.
- In an active program, only start a stage after its `entry_gate` and dependency artifacts are accepted. Complete it only when its `exit_gate` has evidence; update `current_stage` rather than appending operational history.
- Interrupt or stop work whose inputs have become stale; do not let an obsolete Agent finish merely because it already consumed tokens.
- When a continuity capability exists, persist only the `RouteDecision` revision, active assignment IDs and status, source fingerprints, Result Packet locators, integration owner and exact critical-path next action. After compaction or handoff, reconcile those identities before spawning; do not duplicate an Agent whose result is still running or already recorded.

## 7. Failure escalation

Classify a failed result before another spawn:

- `CAPABILITY_MISMATCH`: the slice required reasoning, tools or context beyond the assigned tier.
- `CAPSULE_DEFECT`: objective, scope, inputs or acceptance were ambiguous or contradictory.
- `SOURCE_DRIFT`: the task-relevant source identity changed.
- `INVALID_OBSERVATION`: the tool, fixture, environment or oracle could not test the prediction.
- `CONTRACT_DEFECT`: the shared problem model or acceptance contract was wrong.
- `IMPLEMENTATION_DEFECT`: the stable capsule was understood but the bounded change failed.

After one informative failure, choose exactly one of: repair the capsule, repair one invalid observation, reframe the shared problem, or escalate to a stronger fresh owner. Do not send the same slice to the same capability tier with cosmetic prompt changes.

An escalation's `from_tier` must match the tier of the failed or rejected attempt; `to_tier` must be strictly stronger. Do not manufacture an apparent escalation by misreporting the failed tier.

A primary acceptance rejection is an informative failure. Preserve the rejected diff, violated scope or signal, and evidence; then repair the capsule, reframe under the primary owner, or escalate. A worker's self-reported success does not authorize another same-tier attempt.

The escalation packet contains verified facts, unchanged constraints, source fingerprint, artifacts or diff, exact failure signature, invalidated assumptions, evidence locators and the decision still needed. Exclude unsupported speculation and the previous Agent's hidden reasoning chain.

## 8. Result integration and verification

Require this compact `Result Packet`:

```text
assignment_id and status
verified findings and unresolved uncertainty
artifacts / changed items
source fingerprint and evidence locators
acceptance signals passed / failed
scope or contract conflicts
recommended next decision or escalation request
```

The primary Agent must:

1. Match assignment, source identity, allowed scope and write ownership.
2. Separate facts from inference and compare conflicting results.
3. Map evidence to the parent acceptance matrix; do not count Agent agreement as independent evidence.
4. Emit one explicit acceptance decision whose matrix covers every declared signal; for write slices also confirm artifacts or diff and scope were inspected.
5. Reject rather than integrate stale, out-of-scope, contradictory, or incompletely evidenced work.
6. Inspect shared-contract effects and integrate accepted changes under one owner.
7. Add an independent review only for residual material risk.
8. Validate the coherent integrated stage once, reusing still-valid prior evidence.

## 9. Cost and trajectory metrics

Measure outcomes per task class; do not optimize a single trace.

- Cost: primary and delegated calls, available token / monetary usage, duplicated-read ratio, failed-attempt cost.
- Efficiency: time to first productive action, critical-path duration, idle wait, integration time, coordination-to-work ratio.
- Quality: acceptance pass rate, escaped defects, evidence completeness, reviewer yield, rework after integration.
- Routing: delegation rate, non-delegation accuracy, escalation rate, weak-retry count, maximum concurrency and depth.
- Cascading: economy-write admission rate, primary rejection rate, post-acceptance rework, cost per accepted slice and stronger-tier escalation rate.
- Stability: source-drift stops, overlapping-write incidents, capsule defects, unresolved Result Packets.

Compare `SINGLE_OWNER` against the proposed route on representative tasks. A multi-Agent route is not an improvement when it only moves tokens to hidden threads or improves one benchmark while increasing rework and escaped defects.
