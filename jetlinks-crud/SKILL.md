---
name: jetlinks-crud
description: Implement standard or advanced CRUD work in JetLinks scaffolds. Use when Codex needs to add or modify entities, services, controllers, query flows, batch updates, or CRUD-related side effects while following the local module style.
---

# JetLinks CRUD

Read [`references/common-crud-rules.md`](references/common-crud-rules.md) first.

## Workflow

1. Confirm the target module's execution model and CRUD base abstractions.
2. Follow the smallest existing Entity, Service, and Controller pattern that matches the task.
3. If the task includes complex query, batch processing, or CRUD side effects, read [`references/advanced-crud-rules.md`](references/advanced-crud-rules.md).
4. Pair with `$jetlinks-conventions` or `$jetlinks-reactive` when imports, i18n, or reactive style need extra care.

## Required Constraints

- Do not generate generic CRUD boilerplate that duplicates existing base classes.
- Do not add custom endpoints when the existing query abstraction already covers the use case.
- Prefer moving heavy side effects out of the main CRUD flow.

## Response Shape

1. CRUD scope
2. Existing abstractions to reuse
3. Whether advanced CRUD rules are needed
4. Verification points
