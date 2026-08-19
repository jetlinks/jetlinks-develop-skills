# Evaluation Cases

Use these cases for forward-testing without showing the Agent the expected route. Compare a full-context single owner, orchestration-enabled run, and an ablation that removes the Assignment Capsule or escalation rule.

## Cases

### Short mechanical change

Request: rename one private symbol with exact references and a deterministic test.

Expected property: `SINGLE_OWNER`; no Agent is spawned merely to satisfy the workflow.

### Independent codebase discovery

Request: map backend and frontend owners for one feature before any edit.

Expected property: at most two `PARALLEL_SCOUTS`, disjoint read scopes, evidence locators and one parent integration. No complete repository scan and no writes.

### Stable disjoint implementation

Request: implement two independent adapters after their shared interface and tests are fixed.

Expected property: parallel workers are allowed only with disjoint write sets; the primary owns the shared interface and integration. Validation occurs after integration, not after every edit.

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

Expected property: preserve role boundaries serially and produce the same integration / evidence contract without installing an Agent framework.

## Trace checks

Run [`../scripts/evaluate_orchestration_trace.py`](../scripts/evaluate_orchestration_trace.py) against normalized traces. Include negative traces for:

Each `delegate` event declares `tier: economy | balanced | strong`; an escalation authorizes only a following attempt at the declared higher tier or above.

- missing `RouteDecision` or Assignment Capsule fields;
- delegation depth greater than the declared limit;
- overlapping writes across active write sets;
- successful results without evidence or source fingerprint;
- same-slice retry after failure without an escalation event;
- downward or lateral “escalation” that does not increase capability;
- unresolved Agents or delegated work without final integration.

Track task-level acceptance, escaped defects, total calls / tokens when available, time to first productive action, critical-path duration, coordination ratio, duplicate reads, retries, escalations and maximum concurrency. Do not claim improvement from fewer main-thread tokens alone.
