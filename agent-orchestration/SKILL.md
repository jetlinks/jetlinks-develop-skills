---
name: agent-orchestration
description: 对复杂任务进行环境无关的单 Agent / 多 Agent 路由、真实委派、模型能力分层、并行边界设计、失败升级、结果集成与质量验证。适用于需要在成本、时延和质量之间取舍，或复杂跨模块 / 全栈任务有多个可独立拥有的实质切片，需要由主会话统一设计、冻结公共契约、分阶段委派并集成验收的场景；也适用于拆分独立读密集任务、隔离上下文噪声、分配有界实现或独立审查，以及弱模型反复重试、Agent 职责错位、共享写冲突、汇总缺证据和协调开销膨胀。当前执行路由选中多 Agent 且宿主允许时，必须真实 dispatch、收集并集成，不能只给编排建议；先发现宿主能力，不要求 Codex、特定模型、并发工具、Git、Trellis 或本地文件。不要用于一个 Agent 能低风险直接完成的短小机械任务，或紧耦合、共同根因未知而无法安全分片的工作。
---

# Agent Orchestration

Read [`references/orchestration-and-routing-rules.md`](references/orchestration-and-routing-rules.md) before acting. When reviewing or evolving this workflow, also read [`references/research-basis.md`](references/research-basis.md) and forward-test [`references/evaluation-cases.md`](references/evaluation-cases.md). Read [`references/codex-adapter.md`](references/codex-adapter.md) only when configuring or operating Codex.

## Workflow

1. Freeze the task outcome, invariants, acceptance signals, non-goals, permissions, and integration owner. For an unresolved complex problem, establish a falsifiable problem model before distributing implementation.
2. Discover whether the host can create, steer, wait for, interrupt, and isolate agents; whether model / reasoning / sandbox selection is available; and whether agents share files, tools, credentials, or runtime state. If delegation is unavailable or unsafe, execute the same bounded roles serially under one owner.
3. Create one `RouteDecision` for the current execution from uncertainty, blast radius, coupling, verifiability, failure history, context-isolation value, and expected coordination cost. Choose `SINGLE_OWNER` unless delegation has a concrete quality, critical-path, or context-isolation benefit. A hypothetical future topology is a `ProposedRoute`, not evidence that this task was delegated.
4. Create an `OrchestrationProgram` only when there are at least two substantive, independently ownable slices and a concrete quality, critical-path, or context-isolation benefit. The primary assumes `ORCHESTRATOR_INTEGRATOR`: it owns the problem model, user decisions, public contracts, program transitions, result acceptance, integration, coherent-stage validation, checkpoints and delivery. Otherwise retain `SINGLE_OWNER` or use read-only scouts; do not force a program for a small, tightly coupled, or common-root-cause task.
5. Build the smallest dependency graph that exposes independent slices and the integration point. For a program, move through discovery, design / contract freeze, bounded implementation, integration, independent review when justified, and coherent-stage validation. Each active stage has exactly one current `RouteDecision`; use `PARALLEL_SCOUTS` for bounded read-heavy work, `BOUNDED_WORKER` for one disjoint implementation slice, `INDEPENDENT_REVIEW` for material risk, and `SEQUENTIAL_HANDOFF` for dependent specialties. Do not default to a committee or one Agent per checklist item.
6. Route narrow, low-impact, highly verifiable work to the cheapest capable tier. Admit an economy-tier write only when its contract is frozen, the change is mechanical and reversible, the acceptance oracle is deterministic, its write set is exact and exclusive, and it makes no public-contract, schema, migration, authorization, concurrency, lifecycle, external-side-effect, or unknown-root-cause decision. Keep everything else with a balanced or strong owner. Model names are adapter data, not part of this rule.
7. Give every delegated slice an `Assignment Capsule`: objective and decision, allowed and excluded scope, inputs and source identity, acceptance signals and owner, output contract, budget and stop conditions, and escalation triggers. For economy writes also record execution class, contract state, oracle, risk flags, and reversibility. One owner controls each writable artifact or shared state region.
8. Dispatch implementation only after its relevant shared contracts are frozen, dependencies are satisfied, write sets are mutually exclusive, and acceptance is independently assignable. Otherwise use `SEQUENTIAL_HANDOFF`; the primary may resolve shared-contract or integration conflicts, but must not duplicate a worker's active leaf implementation or overlap its write set.
9. When `RouteDecision.mode != SINGLE_OWNER`, the host exposes safe authorized dispatch, and the capsules are complete, this skill explicitly requires real delegation now: call the host's spawn / dispatch operation, retain an accepted dispatch receipt, collect each terminal `Result Packet`, and integrate it. Do not stop after printing roles, capsules, prompts, or a plan. If dispatch is unavailable, unauthorized, or unsafe, record the concrete `delegation_blocker`, rewrite the current route to `SINGLE_OWNER`, and execute the same bounded roles serially; a delegated mode without an accepted dispatch is invalid.
10. Keep delegation depth at one and begin with at most two active delegated slices unless task evidence justifies more. Children return a compact `Result Packet`; they do not recursively fan out by default or stream raw logs into the main context.
11. Stop a worker on scope drift, source-identity drift, contradictory evidence, invalid observation, permission need, or failed acceptance. After one failed attempt on the same slice, do not retry the same low-capability route with a slightly changed prompt. Escalate fresh facts, failure signature, artifacts, and evidence locators to a stronger owner or reframe the slice.
12. The primary accepts or rejects each worker result after checking source identity, actual artifacts or diff, write scope, and every acceptance signal against evidence. It integrates accepted work, validates the complete coherent stage once, reuses still-valid evidence, and adds an independent reviewer only when impact or uncertainty justifies its cost. Record routing, dispatch, acceptance rejection, escalation, coordination, quality, and critical-path metrics for later tuning.

## Required Constraints

- Do not spawn an Agent merely because tools allow it. Non-delegation is a valid routing result.
- Do not claim or retain a delegated `RouteDecision` from suggested roles or generated prompts. It requires an accepted host dispatch receipt and a terminal result for every dispatched slice.
- Do not use a cheap model for unclear work and compensate with repeated retries. Route by capability floor and escalate after the first informative failure.
- Do not use an economy-tier write merely because its instructions are detailed. Reject it when the task still contains judgment, hidden side effects, shared-contract risk, or a non-deterministic oracle.
- Do not let multiple Agents concurrently write overlapping files, schemas, public contracts, migrations, shared runtime state, or the same external system. A program worker's capsule must cite every shared contract declared for the program and its exact frozen revision before it can write.
- In an `OrchestrationProgram`, do not let the primary enter a competing leaf-implementation action while a worker is active, overlap its write set, or replace result acceptance with raw worker logs. The primary may own public contracts and integration conflicts, and may implement bounded work outside the active-worker window.
- Do not delegate an unresolved common root cause into independent fix attempts. Parallelize evidence collection; keep hypothesis selection and shared repair under one owner.
- Do not transfer a failed Agent's speculative reasoning chain as fact. Transfer verified facts, predictions, failure signatures, source fingerprints, changed artifacts, and evidence locators.
- Do not accept summaries without evidence strong enough for the decision. Syntactic search, inferred relations, tests, runtime traces, and authoritative specifications retain their distinct evidence strength.
- Do not integrate a delegated success without an explicit primary acceptance decision covering every declared acceptance signal. On rejection, repair the capsule, reframe under the primary owner, or escalate; do not retry the same economy route cosmetically.
- Do not let a reviewer silently become a second implementer. A reviewer reports findings and missing evidence; the integration owner decides changes.
- Do not broaden permissions, install orchestration infrastructure, or create persistent state merely to enable delegation.
- Do not validate after every Agent event. Validate once the complete coherent stage has been integrated, unless a discriminating check is required to choose the next route.
- Do not hardcode provider-specific model names, thread APIs, paths, token prices, or concurrency fields into the core routing contract.

## Response Shape

1. `RouteDecision`: selected mode, benefit, risks, and why fewer Agents are insufficient or sufficient
2. Actual dispatch receipts and terminal status, or the concrete delegation blocker and serial fallback; then role assignments, dependency edges, write ownership, concurrency and depth limits
3. Capability tiers and escalation conditions
4. Assignment Capsules and expected Result Packets
5. Integration owner, evidence checks, and coherent-stage validation
6. Cost, latency, quality, coordination, and retry metrics
7. Host limitations, fallback route, and residual risk

For an execution request, this response shape audits what actually happened; producing it is not a substitute for dispatching and completing the selected route.

## Deterministic evaluation

Use [`scripts/evaluate_orchestration_trace.py`](scripts/evaluate_orchestration_trace.py) to check normalized orchestration traces for missing capsules, fan-out, overlapping writes, weak retry loops, evidence-free results, and absent integration. New adapters should emit `schema_version: 2`, which enables dispatch-receipt and primary-acceptance gates; schema version 1 remains readable for existing single-stage traces and is not evidence that a historical trace performed those newer checks. The script accepts stdin or a JSON file, uses only the Python standard library, and never starts Agents or mutates task state.
