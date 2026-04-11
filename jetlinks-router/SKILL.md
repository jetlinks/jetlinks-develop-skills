---
name: jetlinks-router
description: Route JetLinks development requests to the right focused skill in the current workspace. Use when the correct JetLinks skill is unclear, or when a task spans module routing, shared coding conventions, reactive practice, CRUD work, cross-boundary calls, event or subscription flows, and delivery preparation.
---

# JetLinks Router

Read [`ai-prompt.md`](references/ai-prompt.md) first. Treat it as the routing index.

## Workflow

1. Classify the task.
2. Switch to the most relevant focused JetLinks skill.
3. Combine multiple focused skills when the task crosses boundaries.
4. Read adjacent production code before changing anything.
5. Implement complete changes, not pseudo-code.
6. Verify the final solution against the focused skills you used.

## Routing

- Shared coding conventions, imports, and i18n habits: [`../jetlinks-conventions/SKILL.md`](../jetlinks-conventions/SKILL.md)
- Reactive and non-blocking implementation practice: [`../jetlinks-reactive/SKILL.md`](../jetlinks-reactive/SKILL.md)
- Workspace discovery, module placement, and module creation: [`../jetlinks-routing/SKILL.md`](../jetlinks-routing/SKILL.md)
- Standard or advanced CRUD work: [`../jetlinks-crud/SKILL.md`](../jetlinks-crud/SKILL.md)
- Direct dependency, command service, or proxy boundaries: [`../jetlinks-boundary/SKILL.md`](../jetlinks-boundary/SKILL.md)
- Domain events, lifecycle events, and real-time subscriptions: [`../jetlinks-events/SKILL.md`](../jetlinks-events/SKILL.md)
- Branch strategy, commit titles, tests, and PR text: [`../jetlinks-delivery/SKILL.md`](../jetlinks-delivery/SKILL.md)

## Required Constraints

- Do not assume fixed module names, package roots, versions, or resource paths.
- Do not ignore symlinked modules or linked external subprojects when discovering the workspace.
- Prefer local examples over generic memory.
- When local examples are missing, clearly separate defaults from verified workspace facts.
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
3. Edit the code
4. Run the needed tests and collect evidence when relevant
5. Summarize what changed, which focused skills were used, and what was verified
