# Research Basis

This reference records evidence that shaped the workflow. It is not loaded during ordinary routing, and benchmark percentages are not treated as project guarantees.

## Product guidance

- [OpenAI Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) documents built-in and custom Agents, project and personal Agent files, model / reasoning / sandbox overrides, orchestration controls, and the token cost of delegated work. It recommends starting with read-heavy parallel tasks and being cautious with concurrent write-heavy workflows. This supports context isolation, bounded roles, read-first parallelism and explicit concurrency limits.

## Research results

- Chen, Zaharia and Zou, [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176), studies prompt adaptation, approximation and model cascades. It supports choosing the cheapest sufficient capability and escalating selectively rather than sending every task to the strongest model.
- Ong et al., [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665), shows that learned routing can reduce cost while preserving benchmark quality in evaluated settings. It supports dynamic routing, but its single-query results do not by themselves choose multi-Agent topology, write ownership or verification policy.
- Yue et al., [MasRouter: Learning to Route LLMs for Multi-Agent Systems](https://arxiv.org/abs/2502.11133), jointly considers collaboration mode, role allocation and model routing. This directly supports choosing protocol and roles before model tier instead of hardcoding “strong planner, weak executor.”
- Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657), organizes observed failures into system-design issues, inter-Agent misalignment and task-verification failures. This supports Assignment Capsules, explicit integration ownership and evidence-gated acceptance.
- Wang et al., [Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692), demonstrates quality gains from layered aggregation on selected language-model benchmarks. Its architecture also duplicates inference and context, so this skill treats layered committees as an evaluated option rather than a default coding workflow.

## Engineering deductions and limits

The following are operational guardrails derived from the combined evidence, not universal constants proven by any one paper:

- Default delegation depth one and one or two active slices to cap coordination and fan-out.
- Parallelize independent evidence collection before shared implementation.
- After one informative failure, stop cheap same-route retries and transfer a fresh escalation packet.
- Keep public contracts, integration, external side effects and final acceptance under one primary owner.
- Tune thresholds with task-class traces and compare against a single-owner baseline.

Model availability, price, context limits and product configuration change over time. Keep those values in host adapters and re-check the provider's current documentation before updating an adapter.
