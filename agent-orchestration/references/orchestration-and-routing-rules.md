# Orchestration and Routing Rules

## Contents

1. Routing objective
2. Risk and capability routing
3. Collaboration modes
4. Assignment Capsule
5. Execution and write ownership
6. Failure escalation
7. Result integration and verification
8. Cost and trajectory metrics

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
budget: active_slices, depth, read_scope, write_owners, stop_conditions
rationale: concrete comparison with SINGLE_OWNER
```

Use `SINGLE_OWNER` when the rationale is `none`, the work is shorter than a useful handoff, slices are tightly coupled, the same context is required everywhere, or integration risk dominates.

## 2. Risk and capability routing

Assess the capability floor before selecting a model or Agent profile.

| Work shape | Minimum route | Capability guidance |
| --- | --- | --- |
| Exact lookup, bounded scan, formatting, deterministic extraction | `SINGLE_OWNER` or `PARALLEL_SCOUTS` | Cheapest tier that can follow the capsule and cite evidence |
| Read-heavy code mapping with known anchors | `PARALLEL_SCOUTS` | Economical explorer; no edits |
| Disjoint implementation with stable contract and direct tests | `BOUNDED_WORKER` | Balanced worker; one write owner |
| Ambiguous requirements, unknown root cause, shared API / schema / migration | `SINGLE_OWNER` plus optional scouts | Strong primary keeps decision and repair ownership |
| Security, permissions, concurrency, destructive or hard-to-reverse change | Strong primary plus `INDEPENDENT_REVIEW` | High-capability, evidence-focused review |
| One failed bounded attempt or moved failure signature | Fresh escalation or reframe | Do not repeat the same economical route |

Do not equate role with model size. A strong model may execute a critical slice; an economical model may plan a trivial deterministic batch. Route on uncertainty, impact and verification cost.

## 3. Collaboration modes

### `SINGLE_OWNER`

Use for short, coupled, sensitive, or judgment-heavy work. The owner may still use deterministic tools and keep intermediate logs out of the user-facing context.

### `PARALLEL_SCOUTS`

Use for independent evidence collection: separate modules, documents, logs, test families, or risk categories. Give each scout a disjoint question or scope. The parent compares results rather than concatenating them.

### `BOUNDED_WORKER`

Use only after the contract and write set are stable. Assign one coherent implementation slice with named files, symbols, or state ownership. Keep shared contracts and integration with the primary Agent.

### `INDEPENDENT_REVIEW`

Use after a material implementation slice is integrated. The reviewer receives the contract, diff or artifact, acceptance matrix, and evidence locators—not the intended verdict. It returns findings, confidence and missing evidence, and does not edit unless explicitly reassigned.

### `SEQUENTIAL_HANDOFF`

Use when later work depends on a verified artifact from an earlier specialty. Transfer a compact Result Packet and source identity. Do not keep both Agents active when only one can make progress.

## 4. Assignment Capsule

Every delegation must contain:

```text
assignment_id: stable identifier for this slice
objective: observable result, not an activity label
decision: decision this result will enable
allowed_scope: exact files, symbols, sources, systems, or questions
excluded_scope: adjacent work the Agent must not absorb
inputs: anchors, source fingerprint / revision, verified facts, and relevant constraints
acceptance: evidence-backed signals for done
output_contract: Result Packet fields and maximum useful detail
stop_conditions: scope drift, source drift, contradiction, permission need, failed acceptance, or budget exhaustion
escalation_triggers: uncertainty or impact that exceeds the assigned capability floor
permissions: read, write set, external side effects, secrets and approval boundaries
```

An activity such as “inspect the code” is not an objective. Prefer “identify the owner and all direct consumers of symbol X at source fingerprint Y, cite exact locators, and flag unresolved dynamic edges.”

## 5. Execution and write ownership

- Default delegation depth: one. A child requests help through its Result Packet; the primary decides whether to spawn another Agent.
- Default active delegated slices: one or two. Increase only when independent critical-path work remains after integration cost is considered.
- Assign a single owner to each file, public contract, schema, migration, runtime resource, and external side effect.
- Parallelize read-only discovery freely only when scopes and questions are disjoint. Serialize overlapping writes and dependent checks.
- Keep the primary context to contracts, decisions, evidence indexes, conflicts and integrated outputs. Store or cite raw logs at their source.
- Interrupt or stop work whose inputs have become stale; do not let an obsolete Agent finish merely because it already consumed tokens.
- When a continuity capability exists, persist only the `RouteDecision` revision, active assignment IDs and status, source fingerprints, Result Packet locators, integration owner and exact critical-path next action. After compaction or handoff, reconcile those identities before spawning; do not duplicate an Agent whose result is still running or already recorded.

## 6. Failure escalation

Classify a failed result before another spawn:

- `CAPABILITY_MISMATCH`: the slice required reasoning, tools or context beyond the assigned tier.
- `CAPSULE_DEFECT`: objective, scope, inputs or acceptance were ambiguous or contradictory.
- `SOURCE_DRIFT`: the task-relevant source identity changed.
- `INVALID_OBSERVATION`: the tool, fixture, environment or oracle could not test the prediction.
- `CONTRACT_DEFECT`: the shared problem model or acceptance contract was wrong.
- `IMPLEMENTATION_DEFECT`: the stable capsule was understood but the bounded change failed.

After one informative failure, choose exactly one of: repair the capsule, repair one invalid observation, reframe the shared problem, or escalate to a stronger fresh owner. Do not send the same slice to the same capability tier with cosmetic prompt changes.

The escalation packet contains verified facts, unchanged constraints, source fingerprint, artifacts or diff, exact failure signature, invalidated assumptions, evidence locators and the decision still needed. Exclude unsupported speculation and the previous Agent's hidden reasoning chain.

## 7. Result integration and verification

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
4. Inspect shared-contract effects and integrate changes under one owner.
5. Add an independent review only for residual material risk.
6. Validate the coherent integrated stage once, reusing still-valid prior evidence.

## 8. Cost and trajectory metrics

Measure outcomes per task class; do not optimize a single trace.

- Cost: primary and delegated calls, available token / monetary usage, duplicated-read ratio, failed-attempt cost.
- Efficiency: time to first productive action, critical-path duration, idle wait, integration time, coordination-to-work ratio.
- Quality: acceptance pass rate, escaped defects, evidence completeness, reviewer yield, rework after integration.
- Routing: delegation rate, non-delegation accuracy, escalation rate, weak-retry count, maximum concurrency and depth.
- Stability: source-drift stops, overlapping-write incidents, capsule defects, unresolved Result Packets.

Compare `SINGLE_OWNER` against the proposed route on representative tasks. A multi-Agent route is not an improvement when it only moves tokens to hidden threads or improves one benchmark while increasing rework and escaped defects.
