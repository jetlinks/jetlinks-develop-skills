---
name: jetlinks-reactive
description: 在当前 JetLinks 工作区中应用响应式与非阻塞实现实践。适用于需要处理 Mono 或 Flux 链路、避免阻塞调用、批量化响应式 CRUD 副作用，或判断响应式处理器如何与事件、订阅和远程调用协作的场景。
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
- Do not use `CompletableFuture.get(...)`, `Thread.sleep`, or busy-wait loops to coordinate with a reactive result; use `flatMap` / `zip` / `then` / `concatMap` / `Sinks` / events / commands instead.
- Do not bypass reactive context with global mutable `static` state or `ThreadLocal` to fake non-blocking propagation.
- When the reactive API or library does not satisfy the requirement (signature mismatch, missing extension point, serialization error inside the chain), follow [`../jetlinks-conventions/references/root-cause-and-no-hack-rules.md`](../jetlinks-conventions/references/root-cause-and-no-hack-rules.md): solve at the root via official extension points / adjacent abstractions / dependency choice, or inform the user with concrete trade-offs; do not use reflection / visibility hacks / copied source / silent `catch` to make the chain compile.
- When reactive code changes are made, run relevant validation when possible; otherwise state the exact pending commands and residual blocking risks.

## Response Shape

1. Current module execution model
2. Reactive risks or blocking risks
3. Recommended chain or batching pattern
4. Verification evidence or exact pending commands
