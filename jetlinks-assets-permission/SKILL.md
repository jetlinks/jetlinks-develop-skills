---
name: jetlinks-assets-permission
description: 通过 JetLinks AssetsHolder 实现资产数据权限。适用于 CRUD、自定义查询、关联资产、命令、订阅、聚合或批量操作的权限边界，以及 AssetType、AssetsController、权限注入与过滤方式的选择。
---

# JetLinks Assets Permission

Use [`references/assets-holder-rules.md`](references/assets-holder-rules.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

## Workflow

1. Classify the asset-permission scenario: owned CRUD asset, correlated asset, custom endpoint, aggregate query, command boundary, binding or unbinding, subscription or message filtering.
2. Inspect adjacent code for `AssetType` enums, `@AssetsController`, `AssetsHolderCrudController`, `CorrelatesAssetsHolderCrudController`, `CrudAssetPermission`, `AssetsHolder.injectQueryParam`, `AssetsHolder.assertPermission`, command handlers, and local tests.
3. If this is part of a large backend feature, pair with [`../jetlinks-router/references/backend-design-test-driven-rules.md`](../jetlinks-router/references/backend-design-test-driven-rules.md): reuse or record the changed asset type / permission boundary and selected behavior evidence; apply its authorization rule without asking again for an already approved boundary.
4. Choose the unified AssetsHolder integration pattern that matches the local codebase; do not create ad hoc tenant, user, department, organization, or creator filters.
5. Before implementing asset permission code, identify comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md): asset ownership, correlated asset mapping, `ignore = true` equivalent checks, admin / platform exceptions, batch mixed-permission behavior, custom query injection, command or subscription permission propagation.
6. Pair with `$jetlinks-crud`, `$jetlinks-boundary`, `$jetlinks-events`, or `$jetlinks-reactive` when the asset permission decision belongs to those flows.
7. Use [systematic-solving Admission](../systematic-solving/SKILL.md#admission) to decide whether this problem needs structured investigation. It owns hypotheses, evidence and stagnation control; this skill owns the domain implementation. A known cross-layer change or approved retry / mock is not itself an admission signal.

## Required Constraints

- Always prefer the JetLinks `AssetsHolder` asset permission system for data permission control.
- Do not hand-roll data permission filters in CRUD code unless you are implementing or extending an AssetsHolder provider, dimension provider, term builder, asset supplier, or binding provider.
- Do not use `@AssetsController(ignore = true)` on a protected endpoint unless the method performs equivalent `AssetsHolder.injectQueryParam`, `AssetsHolder.assertPermission`, or `AssetsHolder.filterAssets` handling.
- Do not assume the asset type string. Find or add the module's `AssetType` / `EnumAssetType` definition and follow adjacent naming.
- CRUD permissions should normally use `CrudAssetPermission.read`, `save`, `delete`, or `share`; custom permissions require an `AssetPermission` definition and local examples.
- For related assets, verify whether the permission should apply to the entity itself or a referenced asset, then use the correlated-controller or query-injection pattern.
- Treat AssetsHolder as the authoritative owner: when `AssetsHolderCrudController`, `CorrelatesAssetsHolderCrudController`, a command provider, or another established boundary already checks the same action, do not repeat `assertPermission` in Service or callers. A caller checks again only when it is itself an independently exposed security boundary with a distinct subject or action.
- If asset ownership, related asset mapping, permission action, or admin / tenant / platform exception semantics are unclear, ask the user before implementation.
- When this change adds or changes an asset-permission boundary, verify the changed owner with the smallest realistic allow / deny pair. Expand to related fields, batch behavior, or distinct actions only when those semantics differ; do not retest unchanged AssetsHolder framework behavior or bypass the core holder behavior with meaningless mocks.
- Do not leave custom asset permission code comment-free when it encodes non-obvious ownership, correlated asset mapping, `@AssetsController(ignore = true)` replacement checks, admin / platform exceptions, batch mixed-permission behavior, custom query injection, or permission propagation through commands / subscriptions. Add concise comments next to those boundaries.

## Response Shape

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

1. Asset permission scenario
2. Existing AssetsHolder patterns found
3. Asset type and permission action
4. Recommended integration pattern
5. Unclear ownership or scope questions, if any
6. Comment targets added, or the concrete reason no code comments were needed
7. Verification evidence or exact pending commands
