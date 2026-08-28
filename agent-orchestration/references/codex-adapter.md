# Codex Adapter

Use this adapter only for Codex. The core skill remains valid without these files or model names.

## Current Codex capability

OpenAI's current [Codex subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) says local Codex clients can delegate after a direct request or applicable project / skill instruction. Personal custom Agents live under `~/.codex/agents/`; project-scoped Agents live under `.codex/agents/`. Subagents inherit the parent sandbox policy unless an Agent configuration narrows or overrides supported settings.

Current Codex releases enable subagents by default. This repository uses a conservative project baseline that remains useful across clients which support the documented legacy concurrency alias:

```toml
[features]
multi_agent = true

[agents]
max_threads = 3
max_depth = 1
interrupt_message = true
```

Codex configuration schemas evolve across runtimes. The locally validated adapter uses the stable `features.multi_agent` switch and the documented legacy concurrency alias; newer runtimes may also offer `max_concurrent_threads_per_session`, `default_subagent_model`, and `default_subagent_reasoning_effort`. Add richer fields only after the exact runtime that will host the session parses them successfully. The repository profiles already choose their own models, so the portable baseline does not need global model defaults.

The repository includes this project-scoped configuration and four Agent profiles:

- `bounded_explorer`: low-cost, read-only, narrow evidence collection.
- `mechanical_worker`: Luna-backed write worker for frozen, deterministic, low-impact and reversible changes with an exclusive write set.
- `bounded_worker`: balanced, bounded implementation with an assigned disjoint write set.
- `stage_reviewer`: stronger read-only review for material correctness or contract risk.

All four profiles are leaf roles. The locally validated hard capability boundary is the root-level `agents.max_depth = 1`, which applies to the whole Agent tree. The profiles add defense-in-depth instructions to escalate scope needs instead of self-expanding. Do not add an enabled Stage Manager profile to this adapter: the published Codex configuration does not expose a descendant scope / write-set ACL that proves a grandchild is a subset of its parent. Express multiple stages in the primary's `OrchestrationProgram` and dispatch fresh leaves from the primary instead. If a future runtime exposes an enforceable spawn broker or profile-level capability override, validate that exact runtime and policy before enabling it.

Project `.codex/` files configure work performed inside that project; installing only the skill does not silently alter another project's Codex configuration. To reuse the profiles elsewhere, copy or adapt them deliberately at project or personal scope and validate model availability in that host.

## Runtime health gate

Do not treat file presence, `codex --version`, or a model-generated routing plan as proof that subagents work. Before relying on this adapter, verify in order:

1. Identify the exact runtime that hosts the session. An app or IDE may use a bundled Codex executable different from the shell's first `codex` on `PATH`.
2. Make that runtime fully parse its effective configuration. For a CLI that supports it, `codex features list` is a stronger smoke check than `codex --version`, which may return before configuration is decoded.
3. Confirm the primary's effective multi-Agent capability is enabled, the intended profiles are discoverable, and the effective root Agent policy has `max_depth = 1`.
4. Confirm the current session exposes real spawn, collect / wait, steer and interrupt capabilities allowed by its policy.
5. Run a bounded forward test: a qualifying non-`SINGLE_OWNER` route must return an accepted dispatch receipt, terminal Result Packets and one integrated answer. Merely emitting role prompts fails.

If a runtime rejects the current official schema, either upgrade that runtime or use only fields its own parser and documentation accept. Do not copy a newest-version global block into every client, and do not hardcode one historical version's schema into the core skill. Validate each installed client independently.

## Dispatch guidance

- For a qualifying non-`SINGLE_OWNER` current route, this skill is the applicable instruction requesting delegation. Invoke Codex's actual spawn operation after the Assignment Capsule is complete; do not wait for the user to repeat “use subagents”. Retain the returned task / thread acknowledgement as the adapter's `dispatch_receipt`.
- For an `OrchestrationProgram`, keep the main Codex thread as the primary orchestrator and dispatch only the current stage's accepted route. The primary owns shared contracts, integration, acceptance and delivery; it must not run a competing leaf implementation while a worker owns that write set.
- Collect or wait for every dispatched Agent on the current critical path, validate its Result Packet, then integrate. A successful spawn without a consumed result is not a completed delegated route.
- When the optional task-continuity execution adapter is active, let hook events record native dispatch / result-observation receipts, then call its `accept-assignment` only after the primary has checked source identity, write scope, artifacts and every acceptance signal. Do not mark the whole task complete while any recorded dispatch is merely observed, rejected, or still active.
- Ask for `bounded_explorer` only after assigning the shared `decision_question`, one hypothesis, discriminator, evidence axis, read scope, and stop condition. Dispatch at most two in the default evidence round; stop after the primary records `FREEZE`, `ASK_USER`, or `BLOCKER`.
- Ask for `mechanical_worker` only when the contract is frozen, acceptance is deterministic, and its write set is exact and exclusive. Do not use it for public contracts, schemas, migrations, authorization, concurrency, lifecycle, external effects, or unknown root causes; after its first informative failure, collect its evidence and escalate to `bounded_worker` rather than retrying it.
- Ask for `bounded_worker` only after the contract is stable and write ownership is disjoint.
- Ask for `stage_reviewer` only after integration, when the named target is retained and a material residual risk justifies review. Include the task contract, artifact or diff and evidence locators; do not disclose an expected verdict.
- Wait for only the Agents on the current critical path. Steer or interrupt stale work instead of spawning replacements immediately.
- Keep program fan-out at one level. Profiles are reusable leaf execution roles, not nested frontend/backend teams; express the domain, dependencies, frozen contract revisions and exact write ownership in each Assignment Capsule. When a leaf needs work outside its capsule, consume its escalation request and let the primary create a separate leaf assignment. The root `max_depth = 1` hard-stops descendant creation; the prompt is not the security boundary.
- Keep the primary Agent on the user's chosen model unless the host has an explicit, validated routing policy.
- If system policy withholds spawn tools or forbids proactive delegation, revise the current route to `SINGLE_OWNER`, report the blocker, and preserve the same role boundaries serially. Do not simulate a Codex tool call in prose.

Current model names and reasoning levels are adapter choices, not permanent recommendations. If a configured model is unavailable, remove the explicit model to inherit the parent or select a currently supported equivalent using official OpenAI documentation.
