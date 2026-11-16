---
name: jetlinks-reactive
description: 在当前 JetLinks 工作区中应用响应式与非阻塞实践。适用于 Mono / Flux 链路精简、惰性执行、事务与数据库串行操作、有界并发读和背压，以及响应式 CRUD、事件、订阅与远程调用协作。
---

# JetLinks Reactive

Use [`references/reactive-practice.md`](references/reactive-practice.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

## Workflow

1. Inspect adjacent code to confirm whether the target module is reactive or blocking.
2. If this is a new backend feature or large reactive behavior change, first follow [`../jetlinks-router/references/backend-design-test-driven-rules.md`](../jetlinks-router/references/backend-design-test-driven-rules.md): reuse or record the task contract and relevant test goals, apply its authorization rule, and synchronize accepted durable reactive contracts when needed.
3. If the module is reactive, keep `Mono` or `Flux` end-to-end and avoid imperative fallbacks.
4. If blocking I/O is unavoidable, isolate it explicitly and only use the scheduler pattern already accepted by the codebase.
   For database composition, first identify the transaction / connection owner and apply [transaction and concurrency rules](references/reactive-practice.md#事务与数据库并发). Choose fan-out and prefetch from real resource limits, not operator defaults or copied numbers.
5. Before editing non-trivial reactive code, identify comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md): async boundaries, backpressure or collection limits, cancellation / retry / timeout behavior, lifecycle cleanup, tracing context propagation, compatibility, and extracted business stages whose purpose is not obvious from the method name.
6. Combine this skill with `$jetlinks-crud`, `$jetlinks-boundary`, or `$jetlinks-events` when the task spans those scenarios.

## Required Constraints

- Do not call `block()` inside reactive business flows unless the current module already does so for the same boundary and there is no safer local alternative.
- Do not introduce nested `subscribe()` for core business control flow.
- Do not wrap blocking code in reactive types and claim the flow is non-blocking.
- Do not use `CompletableFuture.get(...)`, `Thread.sleep`, or busy-wait loops to coordinate with a reactive result; use `flatMap` / `zip` / `then` / `concatMap` / `Sinks` / events / commands instead.
- Do not bypass reactive context with global mutable `static` state or `ThreadLocal` to fake non-blocking propagation.
- Treat `Publisher` / `Subscriber` / `Subscription` demand, cancellation, and terminal signals as the official reactive boundary. A chain starts at an existing `Publisher` or the first real async I/O boundary, not at a local object.
- Operators must compose clearly named functions. Do not write procedural scripts inside a chain; each `map` / `filter` / `flatMap` / `zip` / `then` should express one semantic step.
- Keep operator chains minimal: avoid `Mono.just(...).map(...)`, adjacent `.map(...).map(...)` for one synchronous business step, `.flatMap(Mono::just)`, identity `map`, redundant `then(Mono.just(...))`, or adjacent `.filter().filter(...)` when the value can be computed before wrapping, synchronous steps can be composed into a named function, `thenReturn(...)` is clearer, or predicates can be combined / extracted.
- Split long Reactor chains by business stage. If a chain mixes validation, permission, command execution, persistence, event publication, and result conversion, keep the chain but move stages into named methods such as `validateAndSendCommand(...)` or `saveLogAndReturn(...)`.
- Do not start a chain with `Mono.just(request)` only to transform a local value before the first async boundary; compute the argument directly and call the reactive API, such as `repository.save(request.toEntity())`.
- For critical reactive business stages, use `MonoTracer` / `FluxTracer` or the existing domain tracer to create manual spans and attributes; route detailed TraceHolder rules to [`../jetlinks-conventions/references/tracing.md`](../jetlinks-conventions/references/tracing.md).
- Do not wrap pure synchronous helpers as `Mono` / `Flux`. Data conversion, field calculation, predicate checks, and other non-I/O logic should remain plain methods and be called from `map`, `filter`, or before entering the chain. Preserve required subscription-time execution, exception signals and Context; `defer` / `fromSupplier` at a genuine lifecycle boundary is not redundant wrapping.
- Do not concurrently execute database operations on the shared connection / session of one transaction. Serial composition or existing batch / set-based operations must preserve the transaction; ordered output from `flatMapSequential` does not serialize execution. Outside that boundary, concurrent reads require justified capacity and ordering semantics.
- Do not call `collectList()` on unbounded or potentially large streams; only collect when the source is clearly bounded by page, limit, batch, protocol size, or validated input size. Prefer pagination, bounded `buffer` / `window`, streaming, or existing query-composition helpers.
- Keep lambdas as glue code. If a lambda contains validation plus query plus mutation plus side effect, nested branching, loops, `try/catch`, or multiple DB / remote calls, extract a named method and test that method through the reactive chain.
- When the reactive API or library does not satisfy the requirement (signature mismatch, missing extension point, serialization error inside the chain), follow [`../jetlinks-conventions/references/root-cause-and-no-hack-rules.md`](../jetlinks-conventions/references/root-cause-and-no-hack-rules.md): solve at the root via official extension points / adjacent abstractions / dependency choice, or inform the user with concrete trade-offs; do not use reflection / visibility hacks / copied source / silent `catch` to make the chain compile.
- Use [systematic-solving Admission](../systematic-solving/SKILL.md#admission) to decide whether this problem needs structured investigation. It owns hypotheses, evidence and stagnation control; this skill owns the domain implementation. A known cross-layer change or approved retry / mock is not itself an admission signal.
- Do not implement a large reactive change until the relevant contract and validation goals are clear under the authorization rule in [backend design](../jetlinks-router/references/backend-design-test-driven-rules.md).
- Do not make reactive tests pass by sleeping, swallowing errors, ignoring dropped signals, or weakening assertions; verify emitted values, completion or error signals, ordering, concurrency, retry, timeout, and side effects that match real usage.
- Do not leave complex reactive chains or extracted reactive stages comment-free when they encode non-obvious async boundaries, batching / backpressure limits, retry / timeout policy, lifecycle cleanup, compatibility, or tracing context propagation. Add concise comments in the code; skip comments for direct `map` / `flatMap` glue with self-explanatory method names.
- When reactive code changes are made, run relevant validation when possible; otherwise state the exact pending commands and residual blocking risks.

## Response Shape

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

1. Current module execution model
2. Reactive risks or blocking risks
3. Official reactive boundary, recommended chain, operator semantics, chain readability, tracing decision, and batching / collection boundary
4. Task-contract path, authoritative-doc sync decision, and test goals when the backend design gate applies
5. Comment targets added, or the concrete reason no code comments were needed
6. Verification evidence or exact pending commands
