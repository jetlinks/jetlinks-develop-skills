---
name: jetlinks-crud
description: 在 JetLinks 脚手架中实现标准或高级 CRUD 开发。适用于需要新增或修改实体、服务、控制器、查询流程、批量更新，或处理与 CRUD 相关副作用，同时遵循当前模块现有风格的场景。
---

# JetLinks CRUD

Use [`references/common-crud-rules.md`](references/common-crud-rules.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

## Workflow

1. Confirm the target module's execution model and CRUD base abstractions.
2. If this is a new backend feature, CRUD change that alters a public contract, ownership, persistence, permission, or batch behavior, first follow [`../jetlinks-router/references/backend-design-test-driven-rules.md`](../jetlinks-router/references/backend-design-test-driven-rules.md): reuse or record the task contract and relevant test goals, apply its authorization rule, and synchronize accepted durable CRUD contracts when needed.
3. Follow the smallest existing Entity, Service, and Controller pattern that matches the task.
4. If the task includes `createQuery()`, `createUpdate()`, `createDelete()`, `QueryParamEntity`, sorting, nested conditions, pagination, AssetsHolder query injection, QueryHelper, complex SQL, native SQL, or multi-query result composition, read [`references/query-dsl-rules.md`](references/query-dsl-rules.md).
5. If the task includes complex query, batch processing, or CRUD side effects, read [`references/advanced-crud-rules.md`](references/advanced-crud-rules.md).
6. If the task includes custom `termType`, QueryParam condition mapping, related-table filters, or `SubTableTermFragmentBuilder`-style exists queries, also read [`references/dynamic-term-rules.md`](references/dynamic-term-rules.md).
7. Pair with `$jetlinks-assets-permission` whenever CRUD query, detail, update, delete, batch operation, export, or custom endpoint needs data permission control through AssetsHolder.
8. Before implementing, identify comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md): public Entity / DTO / Controller / Service contracts, custom endpoints, non-obvious validation, AssetsHolder boundaries, compatibility, batch limits, lifecycle guards, and complex QueryHelper / SQL / DSL decisions.
9. Pair with `$jetlinks-conventions` or `$jetlinks-reactive` when imports, i18n, comments, or reactive style need extra care.
10. Use [systematic-solving Admission](../systematic-solving/SKILL.md#admission) to decide whether this problem needs structured investigation. It owns hypotheses, evidence and stagnation control; this skill owns the domain implementation. A known cross-layer change or approved retry / mock is not itself an admission signal.

## Required Constraints

- Do not generate generic CRUD boilerplate that duplicates existing base classes.
- Do not add custom endpoints when the existing query abstraction already covers the use case.
- Do not hand-roll SQL or private filter DTOs when `createQuery()` / `QueryParamEntity` can express the condition, sorting, pagination, or nested logic.
- Do not concatenate dynamic SQL or manually assemble paged / parent-child query results when `QueryHelper`, `transformPageResult`, or `combineOneToMany` fits the task.
- Do not compress complex CRUD DSL into one unreadable chain. When query construction, permission injection, sorting, pagination, result composition, and side effects mix together, split them into named parameters, query builders, or helper methods.
- Do not write database-dialect-specific SQL unless the user explicitly limits the target database or the module already has that constraint; prefer standard SQL and record dialect risk in docs and PR when unavoidable.
- Do not treat SQL as complete just because it returns correct rows on tiny samples. When a change alters query shape, expected scale, index use, pagination depth, concurrency, batch size, or resource risk, require proportionate pressure, plan, or equivalent performance evidence; SQL keywords alone do not trigger a performance checklist.
- Do not perform row-by-row save / delete when `createUpdate()` / `createDelete()` can express the batch operation; use `setNull(...)` for real null assignment.
- Prefer moving heavy side effects out of the main CRUD flow.
- When Apache Commons utilities are already available in the target module or adjacent CRUD code, prefer them for object, collection, map, and array checks. For string comparison/search/prefix/suffix/plain replace operations, follow `$jetlinks-conventions` and use `Strings.CS` / `Strings.CI` when the dependency provides `Strings`; do not fall back to deprecated `StringUtils` variants. Non-deprecated null-safe predicates such as `StringUtils.isEmpty` / `isBlank` may be used when they match the module's Commons Lang style.
- Do not implement a large CRUD feature until the relevant contract and validation goals are clear under the authorization rule in [backend design](../jetlinks-router/references/backend-design-test-driven-rules.md).
- Treat a new runtime guard as a behavior change. Validate untrusted input at the DTO / framework entry, authoritative AssetsHolder permission at its owning boundary, state or persistence invariants in the service / transaction that owns them, and dangerous empty-condition delete / unbounded query / bulk operations at the operation owner. Do not repeat an established constraint across Controller, Service, Repository, and helpers.
- Trust framework validation, types, and upstream postconditions inside their boundary. Do not add null, not-found, state, permission, or exception-wrapping branches merely for defensive programming, hypothetical callers, or to create an exception test; do not require a per-guard proof artifact when omitting them.
- For any CRUD query, detail, update, delete, batch operation, export, or custom endpoint, analyze whether AssetsHolder data permission control is required. Route implementation details to `$jetlinks-assets-permission`. If asset type, related asset field, permission action, binding relation, or admin / tenant / platform exception semantics are unclear, ask the user before implementation.
- Do not weaken tests to satisfy the CRUD gate. Select only realistic business results, persistence effects, permissions, validation, and regressions that were added or changed; tests cannot create new production validation semantics.
- Do not leave generated CRUD code comment-free when it adds public classes, custom endpoints, permission boundaries, complex query composition, compatibility, batch limits, or non-obvious validation. Add concise code comments at those points; skip comments only for plain fields, standard inherited CRUD, direct DTO mapping, or obvious one-line delegation.
- When CRUD code changes are made, run relevant validation when possible; otherwise state the exact pending commands and remaining CRUD risks.
- For validation, not-found, and conflict errors visible to users, prefer the module's i18n-aware exception pattern over hardcoded exception messages.

## Response Shape

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

1. CRUD scope
2. Existing abstractions to reuse
3. Task-contract path, authoritative-doc sync decision, and test goals when the backend design gate applies
4. Whether advanced CRUD rules are needed
5. Whether Query DSL rules are needed
6. Whether QueryHelper or batch update/delete DSL is needed
7. CRUD DSL readability decision when chains become complex
8. Database portability and performance evidence when SQL is involved
9. Comment targets added, or the concrete reason no code comments were needed
10. Verification evidence or exact pending commands
11. Remaining CRUD risks
