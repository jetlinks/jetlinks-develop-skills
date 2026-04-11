---
name: jetlinks-reactive
description: Apply JetLinks reactive and non-blocking implementation practices in the current workspace. Use when Codex needs to work with Mono or Flux chains, avoid blocking calls, batch reactive CRUD side effects, or decide how reactive handlers should interact with events, subscriptions, and remote calls.
---

# JetLinks Reactive

Read [`references/reactive-practice.md`](references/reactive-practice.md) first.

## Workflow

1. Inspect adjacent code to confirm whether the target module is reactive or blocking.
2. If the module is reactive, keep `Mono` or `Flux` end-to-end and avoid imperative fallbacks.
3. If blocking I/O is unavoidable, isolate it explicitly and only use the scheduler pattern already accepted by the codebase.
4. Combine this skill with `$jetlinks-crud`, `$jetlinks-boundary`, or `$jetlinks-events` when the task spans those scenarios.

## Required Constraints

- Do not call `block()` inside reactive business flows unless the current module already does so for the same boundary and there is no safer local alternative.
- Do not introduce nested `subscribe()` for core business control flow.
- Do not wrap blocking code in reactive types and claim the flow is non-blocking.

## Response Shape

1. Current module execution model
2. Reactive risks or blocking risks
3. Recommended chain or batching pattern
