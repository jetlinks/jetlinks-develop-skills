---
name: agent-orchestration
description: 对复杂任务进行环境无关的单 Agent / 多 Agent 路由、模型能力分层、并行边界设计、委派契约、失败升级、结果集成与质量验证。适用于需要在成本、时延和质量之间取舍，考虑使用 subagent / 多智能体 / 大小模型协作，拆分独立读密集任务、隔离上下文噪声、分配有界实现或独立审查，或已经出现弱模型反复重试、Agent 职责错位、共享写冲突、汇总缺证据和协调开销膨胀的场景；先发现宿主能力，不要求 Codex、特定模型、并发工具、Git、Trellis 或本地文件。不要用于一个 Agent 能低风险直接完成的短小机械任务。
---

# Agent Orchestration

Read [`references/orchestration-and-routing-rules.md`](references/orchestration-and-routing-rules.md) before acting. When reviewing or evolving this workflow, also read [`references/research-basis.md`](references/research-basis.md) and forward-test [`references/evaluation-cases.md`](references/evaluation-cases.md). Read [`references/codex-adapter.md`](references/codex-adapter.md) only when configuring or operating Codex.

## Workflow

1. Freeze the task outcome, invariants, acceptance signals, non-goals, permissions, and integration owner. For an unresolved complex problem, establish a falsifiable problem model before distributing implementation.
2. Discover whether the host can create, steer, wait for, interrupt, and isolate agents; whether model / reasoning / sandbox selection is available; and whether agents share files, tools, credentials, or runtime state. If delegation is unavailable or unsafe, execute the same bounded roles serially under one owner.
3. Create one `RouteDecision` from uncertainty, blast radius, coupling, verifiability, failure history, context-isolation value, and expected coordination cost. Choose `SINGLE_OWNER` unless delegation has a concrete quality, critical-path, or context-isolation benefit.
4. Build the smallest dependency graph that exposes independent slices and the integration point. Prefer `PARALLEL_SCOUTS` for bounded read-heavy work, `BOUNDED_WORKER` for one disjoint implementation slice, `INDEPENDENT_REVIEW` for material risk, and `SEQUENTIAL_HANDOFF` for dependent specialties. Do not default to a committee or one Agent per checklist item.
5. Route narrow, low-impact, highly verifiable work to the cheapest capable tier. Keep ambiguous architecture, shared contracts, security, migrations, concurrency, destructive actions, unknown root causes, and failed escalations with a stronger owner. Model names are adapter data, not part of this rule.
6. Give every delegated slice an `Assignment Capsule`: objective and decision, allowed and excluded scope, inputs and source identity, acceptance signals, output contract, budget and stop conditions, and escalation triggers. One owner controls each writable artifact or shared state region.
7. Keep delegation depth at one and begin with at most two active delegated slices unless task evidence justifies more. Children return a compact `Result Packet`; they do not recursively fan out by default or stream raw logs into the main context.
8. Stop a worker on scope drift, source-identity drift, contradictory evidence, invalid observation, permission need, or failed acceptance. After one failed attempt on the same slice, do not retry the same low-capability route with a slightly changed prompt. Escalate fresh facts, failure signature, artifacts, and evidence locators to a stronger owner or reframe the slice.
9. Keep the primary Agent responsible for shared contracts, user decisions, integration, external side effects, acceptance mapping, and delivery. Treat every subagent result as untrusted until its scope, source identity, evidence, uncertainty, and conflicts are checked.
10. Validate the integrated result at a coherent stage boundary. Reuse still-valid evidence, add an independent reviewer only when impact or uncertainty justifies its cost, then record routing, escalation, coordination, quality, and critical-path metrics for later tuning.

## Required Constraints

- Do not spawn an Agent merely because tools allow it. Non-delegation is a valid routing result.
- Do not use a cheap model for unclear work and compensate with repeated retries. Route by capability floor and escalate after the first informative failure.
- Do not let multiple Agents concurrently write overlapping files, schemas, public contracts, migrations, shared runtime state, or the same external system.
- Do not delegate an unresolved common root cause into independent fix attempts. Parallelize evidence collection; keep hypothesis selection and shared repair under one owner.
- Do not transfer a failed Agent's speculative reasoning chain as fact. Transfer verified facts, predictions, failure signatures, source fingerprints, changed artifacts, and evidence locators.
- Do not accept summaries without evidence strong enough for the decision. Syntactic search, inferred relations, tests, runtime traces, and authoritative specifications retain their distinct evidence strength.
- Do not let a reviewer silently become a second implementer. A reviewer reports findings and missing evidence; the integration owner decides changes.
- Do not broaden permissions, install orchestration infrastructure, or create persistent state merely to enable delegation.
- Do not validate after every Agent event. Validate once the complete coherent stage has been integrated, unless a discriminating check is required to choose the next route.
- Do not hardcode provider-specific model names, thread APIs, paths, token prices, or concurrency fields into the core routing contract.

## Response Shape

1. `RouteDecision`: selected mode, benefit, risks, and why fewer Agents are insufficient or sufficient
2. Agent / role assignments, dependency edges, write ownership, concurrency and depth limits
3. Capability tiers and escalation conditions
4. Assignment Capsules and expected Result Packets
5. Integration owner, evidence checks, and coherent-stage validation
6. Cost, latency, quality, coordination, and retry metrics
7. Host limitations, fallback route, and residual risk

## Deterministic evaluation

Use [`scripts/evaluate_orchestration_trace.py`](scripts/evaluate_orchestration_trace.py) to check normalized orchestration traces for missing capsules, fan-out, overlapping writes, weak retry loops, evidence-free results, and absent integration. The script accepts stdin or a JSON file, uses only the Python standard library, and never starts Agents or mutates task state.
