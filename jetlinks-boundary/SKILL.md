---
name: jetlinks-boundary
description: 在当前 JetLinks 工作区中选择并实现跨边界交互方式。适用于需要在直接依赖、命令服务、代理或其他跨模块访问模式之间做决策和落地的场景，尤其是响应式模块或低上下文脚手架中的边界选择。
---

# JetLinks Boundary

Read [`references/module-reference.md`](references/module-reference.md) first.

## Workflow

1. Identify the capability boundary that the task needs to cross.
2. Confirm whether the current workspace already has command services, proxies, support IDs, or concrete command classes.
3. Read [`references/cross-service-call-rules.md`](references/cross-service-call-rules.md) before implementing providers or consumers.
4. Keep the chosen pattern aligned with the module's execution model, existing naming scheme, and local command invocation style.

## Required Constraints

- Do not invent command IDs, service IDs, support IDs, or proxy contracts.
- Do not directly inject another boundary's internal implementation class.
- When local command classes already exist, prefer explicit command objects with `commandSupport.execute(...)` over shortcut calls such as `executeToMono(...)`.
- In reactive modules, keep the cross-boundary call non-blocking.
- When boundary code changes are made, run relevant validation when possible; otherwise state the exact pending commands and cross-boundary risks.

## Response Shape

1. Boundary to cross
2. Existing mechanisms found in the workspace
3. Recommended interaction pattern
4. Rejected patterns and reasons
5. Verification evidence or exact pending commands
