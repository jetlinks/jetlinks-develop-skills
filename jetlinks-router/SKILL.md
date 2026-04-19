---
name: jetlinks-router
description: 将 JetLinks 开发请求路由到当前工作区中最合适的 focused skill。适用于尚不确定应使用哪个 JetLinks 技能，或任务同时涉及模块落点、通用编码规范、响应式实践、CRUD、跨边界调用、事件与订阅流程、前端页面改造以及交付准备的场景。
---

# JetLinks Router

Read [`ai-prompt.md`](references/ai-prompt.md) first. Treat it as the routing index.

## Workflow

1. Classify the task.
2. Switch to the most relevant focused JetLinks skill.
3. Combine multiple focused skills when the task crosses boundaries.
4. Read adjacent production code before changing anything.
5. Implement complete changes, not pseudo-code.
6. Verify the final solution against the focused skills you used, and when code changes are involved run the relevant validation or state the exact pending command and residual risk.
7. If the finished task produced reusable knowledge, route to `jetlinks-capture`, give the recommendation first, and only write the document after user confirmation.
8. If the captured result is generic enough to become a shared JetLinks skill, ask whether to merge it into `jetlinks-develop-skills` and prepare an upstream PR.

## Routing

- Protocol package registration, transport codecs, and binary packet handling: [`../jetlinks-protocol/SKILL.md`](../jetlinks-protocol/SKILL.md)
- Shared coding conventions, imports, and i18n habits: [`../jetlinks-conventions/SKILL.md`](../jetlinks-conventions/SKILL.md)
- Reactive and non-blocking implementation practice: [`../jetlinks-reactive/SKILL.md`](../jetlinks-reactive/SKILL.md)
- Workspace discovery, module placement, and module creation: [`../jetlinks-routing/SKILL.md`](../jetlinks-routing/SKILL.md)
- Standard or advanced CRUD work: [`../jetlinks-crud/SKILL.md`](../jetlinks-crud/SKILL.md)
- Direct dependency, command service, or proxy boundaries: [`../jetlinks-boundary/SKILL.md`](../jetlinks-boundary/SKILL.md)
- Domain events, lifecycle events, and real-time subscriptions: [`../jetlinks-events/SKILL.md`](../jetlinks-events/SKILL.md)
- Frontend page implementation, capability reuse, and quality constraints in JetLinks Web: [`../jetlinks-web/SKILL.md`](../jetlinks-web/SKILL.md)
- Knowledge capture and reusable summary output: [`../jetlinks-capture/SKILL.md`](../jetlinks-capture/SKILL.md)
- Branch strategy, commit titles, tests, and PR text: [`../jetlinks-delivery/SKILL.md`](../jetlinks-delivery/SKILL.md)

## Required Constraints

- Do not assume fixed module names, package roots, versions, or resource paths.
- Do not ignore symlinked modules or linked external subprojects when discovering the workspace.
- Prefer local examples over generic memory.
- When local examples are missing, clearly separate defaults from verified workspace facts.
- When Apache Commons utilities are already present or adjacent code already uses them, prefer them for common null or empty checks instead of handwritten repetitive branches.
- Keep changes scoped to the requested capability; avoid unrelated refactors or speculative cleanup.
- Prefer existing framework abstractions and focused skills over adding new ad hoc guidance here.

## Response Shape

When analyzing first:

1. Task classification
2. Focused JetLinks skill or skills to use
3. Workspace facts to confirm
4. Proposed code locations

When implementing:

1. Quietly classify and inspect
2. Load the needed focused skill or skills
3. Edit the code with the smallest consistent change
4. Run the needed validation when possible, otherwise state the exact pending commands and residual risks
5. Summarize what changed, which focused skills were used, what was verified, whether knowledge capture is recommended, and whether it is worth promoting into the official skills repository
