---
name: jetlinks-secondary-development
description: Analyze and implement JetLinks-based scaffold tasks in the current workspace. Use when Codex needs to create or modify modules, CRUD code, command services, event-driven logic, realtime subscriptions, i18n, imports, or module boundaries while following the local .prompt rules and existing code conventions.
---

# JetLinks Secondary Development

Read [`ai-prompt.md`](references/ai-prompt.md) first. Treat it as the routing index.

## Workflow

1. Classify the task.
2. If the workspace structure is unclear, open [`references/module-list.md`](references/module-list.md).
3. Load only the minimum reference files needed for the task.
4. Read adjacent production code before changing anything.
5. If a candidate module is a symbolic link, inspect both the linked workspace path and the real target path.
6. Follow the local module's reactive/blocking style, import family, and naming.
7. Implement complete changes, not pseudo-code.
8. Verify dependencies, imports, permissions, i18n, and boundary choices before finishing.
9. If the repository is only a scaffold with little or no reference code, switch to a minimal scaffold mode and generate the first compliant example instead of stopping.

## Routing

- Unknown module, directory, or capability location: [`references/module-list.md`](references/module-list.md)
- Unsure whether to use direct dependency, command service, event, or subscription: [`references/module-reference.md`](references/module-reference.md)
- Need annotation or import confirmation: [`references/annotations-and-imports-reference.md`](references/annotations-and-imports-reference.md)
- Creating a new module: [`references/module-creation-rules.md`](references/module-creation-rules.md)
- Standard CRUD work: [`references/common-crud-rules.md`](references/common-crud-rules.md)
- Complex CRUD, query, batch, or sync logic: [`references/advanced-crud-rules.md`](references/advanced-crud-rules.md)
- Cross-boundary calls or command providers: [`references/cross-service-call-rules.md`](references/cross-service-call-rules.md)
- Topic/message subscriptions: [`references/realtime-subscription-rules.md`](references/realtime-subscription-rules.md)
- Entity lifecycle or domain events: [`references/event-driven-rules.md`](references/event-driven-rules.md)
- User-facing text and localization: [`references/i18n.md`](references/i18n.md)

## Required Constraints

- Do not assume fixed module names, package roots, versions, or resource paths.
- Do not ignore symlinked modules or linked external subprojects when discovering the workspace.
- Do not invent service IDs, command IDs, topics, or import packages.
- Prefer local examples over generic memory.
- When local examples are missing, fall back to the local pom/layout plus the bundled `references/` rules, and clearly separate defaults from verified workspace facts.
- In low-context scaffolds, prefer event-driven side effects over inline CRUD orchestration, and prefer direct dependency over command boundaries unless the command framework is already present or explicitly requested.
- Prefer existing framework abstractions over new custom patterns.
- Add i18n only when the current module or scaffold already uses that convention, or the user explicitly asks for it.

## Response Shape

When analyzing first:

1. Task classification
2. Rule files to load
3. Workspace facts to confirm
4. Proposed code locations

When implementing:

1. Quietly classify and inspect
2. Load the needed reference files
3. Edit the code
4. Summarize what changed, which reference files were used, and what was verified
