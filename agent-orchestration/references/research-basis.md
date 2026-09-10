# Research Basis

This reference records evidence that shaped the workflow. It is not loaded during ordinary routing, and benchmark percentages are not treated as project guarantees.

## Product guidance

- [OpenAI Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) documents built-in and custom Agents, inherited configuration, model / reasoning / sandbox overrides, orchestration controls, and the token cost of delegated work. Together with the locally validated Codex `agents.max_depth` host control, this supports context isolation, bounded roles, read-first parallelism, explicit concurrency limits, and hard-stopping recursive fan-out instead of relying only on instructions.

## Research results

- Chen, Zaharia and Zou, [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176), studies prompt adaptation, approximation and model cascades. It supports choosing the cheapest sufficient capability and escalating selectively rather than sending every task to the strongest model.
- Ong et al., [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665), shows that learned routing can reduce cost while preserving benchmark quality in evaluated settings. It supports dynamic routing, but its single-query results do not by themselves choose multi-Agent topology, write ownership or verification policy.
- Yue et al., [MasRouter: Learning to Route LLMs for Multi-Agent Systems](https://arxiv.org/abs/2502.11133), jointly considers collaboration mode, role allocation and model routing. This directly supports choosing protocol and roles before model tier instead of hardcoding “strong planner, weak executor.”
- Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657), organizes observed failures into system-design issues, inter-Agent misalignment and task-verification failures. This supports Assignment Capsules, explicit integration ownership and evidence-gated acceptance.
- Wang et al., [Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692), demonstrates quality gains from layered aggregation on selected language-model benchmarks. Its architecture also duplicates inference and context, so this skill treats layered committees as an evaluated option rather than a default coding workflow.

## Engineering deductions and limits

The following are operational guardrails derived from the combined evidence, not universal constants proven by any one paper:

- Default delegation depth one and one or two active slices to cap coordination and fan-out.
- Treat scope, permissions, write ownership and budget as monotonically decreasing capabilities. Allow nested delegation only when a host policy can enforce that attenuation before spawn; otherwise make delegated roles leaves.
- Parallelize independent evidence collection before shared implementation.
- Bind each evidence round to one decision question and stop after discriminating evidence; additional broad scouts add coordination and duplicated-reading cost without changing stage admission. The default limit of two scouts is an operational budget to tune by task class, not a benchmark claim.
- Represent substantial cross-module delivery as a bounded sequence of stage-level routing decisions; keep one primary orchestrator responsible for shared contracts, integration and acceptance instead of creating recursive Agent teams.
- Freeze the relevant cross-slice contract revision and satisfy dependency gates before concurrent implementation writes; otherwise use a sequential handoff.
- Treat review as a conditional risk-control stage for a retained integration candidate, not a mandatory committee step for every provisional design.
- Keep control-plane verification proportional to the activated risk. Central defaults may expand a compact depth-one assignment deterministically; do not spend model work restating them or create new evidence solely to populate orchestration records.
- After one informative failure, stop cheap same-route retries and transfer a fresh escalation packet.
- Keep public contracts, integration, external side effects and final acceptance under one primary owner.
- Tune thresholds with task-class traces and compare against a single-owner baseline.

Model availability, price, context limits and product configuration change over time. Keep those values in host adapters and re-check the provider's current documentation before updating an adapter.
