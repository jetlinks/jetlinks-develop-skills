---
name: jetlinks-events
description: Implement JetLinks event-driven and subscription-based flows. Use when Codex needs to add entity lifecycle listeners, domain events, topic subscriptions, message handlers, or other asynchronous side effects in the current workspace.
---

# JetLinks Events

Read [`references/event-driven-rules.md`](references/event-driven-rules.md) first.

## Workflow

1. Confirm whether the task is a lifecycle event, domain event, or continuous subscription flow.
2. For entity or business side effects, follow [`references/event-driven-rules.md`](references/event-driven-rules.md).
3. For Topic, EventBus, or message-stream handlers, follow [`references/realtime-subscription-rules.md`](references/realtime-subscription-rules.md).
4. Pair with `$jetlinks-reactive` or `$jetlinks-crud` when the flow also touches reactive chains or CRUD logic.

## Required Constraints

- Do not turn synchronous query requirements into fake subscription flows.
- Do not publish external side effects before the chosen transaction boundary is safe.
- Keep handlers idempotent and avoid circular triggers.

## Response Shape

1. Flow type
2. Trigger timing or subscription source
3. Handler pattern to follow
4. Event or message risks to verify
