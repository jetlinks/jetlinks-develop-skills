---
name: jetlinks-router
description: 将 JetLinks 开发请求路由到当前工作区中最合适的 focused skill。适用于尚不确定应使用哪个 JetLinks 技能，或任务同时涉及模块落点、通用编码规范、响应式实践、CRUD、跨边界调用、事件与订阅流程、前端页面改造以及交付准备的场景。
---

# JetLinks Router

Read [`ai-prompt.md`](references/ai-prompt.md) first. Treat it as the routing index.

## Workflow

1. Classify the task.
2. Decide whether the task must enter a plan-first gate. Use it for complex, cross-module, multi-subtask, or still-changing requirements.
3. When plan-first is required, output a concise plan that covers goal, scope, non-goals, steps, risks or pending confirmations, and validation, then wait for user confirmation before implementation.
4. Switch to the most relevant focused JetLinks skill.
5. Combine multiple focused skills when the task crosses boundaries.
6. Read adjacent production code before changing anything.
7. Implement complete changes, not pseudo-code.
8. Verify the final solution against the focused skills you used, and when code changes are involved run the relevant validation or state the exact pending command and residual risk.
9. If the finished task produced reusable knowledge, route to `jetlinks-capture`, give the recommendation first, and only write the document after user confirmation.
10. If the captured result is generic enough to become a shared JetLinks skill, ask whether to merge it into `jetlinks-develop-skills` and prepare an upstream PR.

## Routing

- Protocol package registration, transport codecs, and binary packet handling: [`../jetlinks-protocol/SKILL.md`](../jetlinks-protocol/SKILL.md)
- Shared coding conventions, imports, and i18n habits: [`../jetlinks-conventions/SKILL.md`](../jetlinks-conventions/SKILL.md)
- Reactive and non-blocking implementation practice: [`../jetlinks-reactive/SKILL.md`](../jetlinks-reactive/SKILL.md)
- Workspace discovery, module placement, and module creation: [`../jetlinks-routing/SKILL.md`](../jetlinks-routing/SKILL.md)
- Standard or advanced CRUD work: [`../jetlinks-crud/SKILL.md`](../jetlinks-crud/SKILL.md)
- Direct dependency, command service, or proxy boundaries: [`../jetlinks-boundary/SKILL.md`](../jetlinks-boundary/SKILL.md)
- Domain events, lifecycle events, and real-time subscriptions: [`../jetlinks-events/SKILL.md`](../jetlinks-events/SKILL.md)
- Frontend page implementation, capability reuse, and quality constraints in JetLinks Web: [`../jetlinks-web/SKILL.md`](../jetlinks-web/SKILL.md). First analyze the real business workflow instead of defaulting to backend CRUD. Treat references as supporting material from adjacent pages or similar business scenarios, keep Ant Design as the baseline style, avoid meaningless decorative data, and make sure prototype annotations stay out of the final user-facing UI.
- Frontend page style selection and structural reuse: [`../jetlinks-web-style/SKILL.md`](../jetlinks-web-style/SKILL.md). Use it when the user wants to follow an existing page style, when a page could reasonably be built in several different shells, or when style choice should be confirmed before implementation.
- Knowledge capture and reusable summary output: [`../jetlinks-capture/SKILL.md`](../jetlinks-capture/SKILL.md)
- Branch strategy, commit titles, tests, and PR text: [`../jetlinks-delivery/SKILL.md`](../jetlinks-delivery/SKILL.md)

## Required Constraints

- Do not assume fixed module names, package roots, versions, or resource paths.
- Do not ignore symlinked modules or linked external subprojects when discovering the workspace.
- Prefer local examples over generic memory.
- When local examples are missing, clearly separate defaults from verified workspace facts.
- Do not directly implement complex or unstable requirements before clarifying scope, exclusions, risks, and validation with the user.
- When Apache Commons utilities are already present or adjacent code already uses them, prefer them for common null or empty checks instead of handwritten repetitive branches.
- Keep changes scoped to the requested capability; avoid unrelated refactors or speculative cleanup.
- If the tool supports a dedicated Plan mode, prefer it for plan-first tasks; otherwise still follow the same behavior manually.
- Prefer existing framework abstractions and focused skills over adding new ad hoc guidance here.

## Response Shape

When analyzing first:

1. Task classification
2. Whether plan-first confirmation is required
3. Focused JetLinks skill or skills to use
4. Workspace facts to confirm
5. Proposed code locations
6. Plan summary or direct-execution rationale

When implementing:

1. Quietly classify and inspect
2. If plan-first applies, output the plan and wait for confirmation
3. Load the needed focused skill or skills
4. Edit the code with the smallest consistent change
5. Run the needed validation when possible, otherwise state the exact pending commands and residual risks
6. Summarize what changed, which focused skills were used, what was verified, whether knowledge capture is recommended, and whether it is worth promoting into the official skills repository
