---
name: jetlinks-boundary
description: Choose and implement JetLinks cross-boundary interaction patterns. Use when Codex needs to decide between direct dependency, command service, proxy, or other cross-module access patterns, especially in reactive or low-context scaffolds.
---

# JetLinks Boundary

Read [`references/module-reference.md`](references/module-reference.md) first.

## Workflow

1. Identify the capability boundary that the task needs to cross.
2. Confirm whether the current workspace already has command services, proxies, or support IDs.
3. Read [`references/cross-service-call-rules.md`](references/cross-service-call-rules.md) before implementing providers or consumers.
4. Keep the chosen pattern aligned with the module's execution model and existing naming scheme.

## Required Constraints

- Do not invent command IDs, service IDs, support IDs, or proxy contracts.
- Do not directly inject another boundary's internal implementation class.
- In reactive modules, keep the cross-boundary call non-blocking.

## Response Shape

1. Boundary to cross
2. Existing mechanisms found in the workspace
3. Recommended interaction pattern
4. Rejected patterns and reasons
