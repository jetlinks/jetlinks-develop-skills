# Codex Adapter

Use this adapter only for Codex. The core skill remains valid without these files or model names.

## Current Codex capability

OpenAI's current [Codex subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) says local Codex clients can delegate after a direct request or applicable project / skill instruction. Personal custom Agents live under `~/.codex/agents/`; project-scoped Agents live under `.codex/agents/`. Subagents inherit the parent sandbox policy unless an Agent configuration narrows or overrides supported settings.

Global controls use `[agents]` in Codex configuration:

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 3
default_subagent_model = "gpt-5.6-terra"
default_subagent_reasoning_effort = "medium"
interrupt_message = true
```

The repository includes this project-scoped configuration and three Agent profiles:

- `bounded_explorer`: low-cost, read-only, narrow evidence collection.
- `bounded_worker`: balanced, bounded implementation with an assigned disjoint write set.
- `stage_reviewer`: stronger read-only review for material correctness or contract risk.

Project `.codex/` files configure work performed inside that project; installing only the skill does not silently alter another project's Codex configuration. To reuse the profiles elsewhere, copy or adapt them deliberately at project or personal scope and validate model availability in that host.

## Dispatch guidance

- Ask for `bounded_explorer` only after assigning exact questions and scopes.
- Ask for `bounded_worker` only after the contract is stable and write ownership is disjoint.
- Ask for `stage_reviewer` after integration, with the task contract, artifact or diff and evidence locators. Do not disclose an expected verdict.
- Wait for only the Agents on the current critical path. Steer or interrupt stale work instead of spawning replacements immediately.
- Keep the primary Agent on the user's chosen model unless the host has an explicit, validated routing policy.

Current model names and reasoning levels are adapter choices, not permanent recommendations. If a configured model is unavailable, remove the explicit model to inherit the parent or select a currently supported equivalent using official OpenAI documentation.
