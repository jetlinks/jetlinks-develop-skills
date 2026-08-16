---
name: jetlinks-events
description: 在当前 JetLinks 工作区中实现事件驱动和订阅处理流程。适用于需要新增实体生命周期监听、领域事件、主题订阅、消息处理器，或其他异步副作用逻辑的场景。
---

# JetLinks Events

Read [`references/event-driven-rules.md`](references/event-driven-rules.md) first.

## Workflow

1. Confirm whether the task is a lifecycle event, domain event, or continuous subscription flow.
2. If this is a new backend feature, large behavior change, or event flow spanning multiple modules, first follow [`../jetlinks-router/references/backend-design-test-driven-rules.md`](../jetlinks-router/references/backend-design-test-driven-rules.md): record the task contract and realistic test goals in Trellis or the chosen Git-ignored runtime artifact, wait for explicit user confirmation, then update authoritative docs only for accepted durable event contracts.
3. For entity or business side effects, follow [`references/event-driven-rules.md`](references/event-driven-rules.md).
4. For Topic, EventBus, or message-stream handlers, follow [`references/realtime-subscription-rules.md`](references/realtime-subscription-rules.md).
5. Before implementing handlers, identify comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md): trigger timing, transaction boundary, idempotency, loop prevention, replay handling, batch / backpressure limits, Topic compatibility, and subscription lifecycle cleanup.
6. Pair with `$jetlinks-reactive` or `$jetlinks-crud` when the flow also touches reactive chains or CRUD logic.
7. Pair with `$systematic-solving` when a timing, idempotency, replay, ordering, lifecycle, or multi-consumer issue has competing root causes, or a first implementation only moves the failure. Do not add another retry, delay, deduplication branch, or mock before rebuilding the event-flow hypothesis.

## Required Constraints

- Do not turn synchronous query requirements into fake subscription flows.
- Do not publish external side effects before the chosen transaction boundary is safe.
- Keep handlers idempotent and avoid circular triggers.
- Do not implement a large event or subscription change before the task contract, event timing, idempotency strategy, and realistic test goals have been documented and confirmed.
- Do not weaken asynchronous assertions just to pass tests; verify trigger conditions, emitted event or message content, idempotency, transaction timing, and failure or retry behavior that matter to real usage.
- Do not leave event handlers, subscribers, or message processors comment-free when they rely on non-obvious trigger timing, transaction-after-commit behavior, idempotency, replay tolerance, loop prevention, Topic compatibility, batching, or lifecycle cleanup. Add concise code comments at those boundaries; skip comments for simple one-step event forwarding.
- When event or subscription code changes are made, run relevant validation when possible; otherwise state the exact pending commands and event-chain risks.

## Response Shape

1. Flow type
2. Trigger timing or subscription source
3. Handler pattern to follow
4. Task-contract path, authoritative-doc sync decision, and test goals when the backend design gate applies
5. Event or message risks to verify
6. Comment targets added, or the concrete reason no code comments were needed
7. Verification evidence or exact pending commands
