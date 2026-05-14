---
name: jetlinks-web-style
description: 为 JetLinks 前端页面选择、复用并约束业务交互方案。这是 JetLinks 前端交互方案选择的核心入口。除非任务属于"局部调整白名单"（改一个字段 / 改一个筛选条件 / 改一个弹窗 / 仅样式与文案 props 微调），任何新增页面、重构页面壳层、调整信息架构或主筛选 / 主列表 / 主详情承载都必须先在 `style-catalog.md`（索引）+ `style-catalog-templates.md`（13 个方案，按需只读候选对应 `###` 小节）中给用户 2-4 个具体业务选项再实现，并按 `style-catalog-routing.md` 的统一字段（业务任务 / 首屏 ASCII 线框 / 信息密度 / 编辑梯度 / 核心组件 / 状态锚点 / 不借鉴清单）稳定复用结构与 `jetlinks-web-core` 组件组合，禁止默认回退成"传统后台表格 + 编辑弹窗"套壳。防爆上下文：不要整篇加载 `style-catalog-templates.md`，选型阶段读 `style-catalog-routing.md` + `style-catalog-core.md` 即可。
---

# JetLinks Web Style

Read [`references/style-selection-rules.md`](references/style-selection-rules.md) first. Solution selection is **mandatory by default**; only the local-tweak whitelist may skip it.

## Workflow

1. Read [`references/style-selection-rules.md`](references/style-selection-rules.md) and determine whether this task hits the **local-tweak whitelist** (single form field, single filter chip, single dialog content, styling/copy/props-only). If it does, hand back to `../jetlinks-web/SKILL.md` for direct implementation. Otherwise, the rest of this workflow is mandatory.
2. If the user already named a solution, reference page, or said "按当前资产页这种结构", map it directly to the closest solution in [`references/style-catalog-templates.md`](references/style-catalog-templates.md) (read only the matching `###` section) and continue.
3. Unless the task hits the local-tweak whitelist, you must present 2-4 concrete business solutions from [`references/style-catalog-templates.md`](references/style-catalog-templates.md) and wait for the user's choice—**load only the `###` subsections for those candidates**, not the full file. Do not silently default to a CRUD shell. Do not ask an open-ended design question.
4. Pick solutions using [`references/style-catalog-routing.md`](references/style-catalog-routing.md)'s "业务任务 → 方案路由" table; identify the user's first task on the page first, then map to 2-4 candidates from the corresponding group.
5. For each option, describe the business fit, first-screen ASCII skeleton, information density target, edit trigger gradient, core `jetlinks-web-core` components, state/label anchor, main action placement, and what should not be borrowed from unrelated pages.
6. After the user chooses, record a compact solution profile in your working notes: solution name, primary filter surface, content surface, detail carrier, edit mode, core components, action placement, density target, and sidebar mode.
7. Restate the anti-admin-shell hard constraints from [`references/style-catalog-core.md`](references/style-catalog-core.md) that apply to the chosen solution (edit trigger gradient, no-stack first screen + **one main visual anchor per screen**, state-before-fields + **no single-side colored bar as primary status signal**, density target, modal-is-not-the-only-edit-path; when the solution carries a single-object detail header, the "详情页头部摘要区" rule: name/description inline editable, tags added/removed in place, status switched via quick actions, no "编辑按钮 → 基本信息表单"; always the "编辑交互样式统一" rule: per-field-type fixed component mapping with identical trigger and save behavior across modules, no bespoke editable text / chip / inline form / validation bubble when `jetlinks-web-core` already exposes one; when the solution carries an object detail page, also apply the "详情页 10 条硬规则" + AI 味 7 条不要 + 反向引用做主区段; when the solution introduces a sidebar, apply the two-tier active-state rule + the 8 collapsible-group etiquette rules; for top-level tab root routes, do not render PageHead; for floating elements, tokenized z-index and single-FAB-per-page), so implementation does not drift.
8. Hand implementation back to `../jetlinks-web/SKILL.md`, but keep the chosen solution profile stable unless the user explicitly changes it; component availability must still be verified from the target workspace `jetlinks-web-core`.
9. When the user says "复用现在这种风格", treat it as a request to reuse the closest business interaction solution; match the existing structure and interaction skeleton instead of inventing a visually different page shell.
10. When a new reusable solution emerges, extend [`references/style-catalog-templates.md`](references/style-catalog-templates.md) with a new `###` section (and update the index table in [`references/style-catalog.md`](references/style-catalog.md) if needed) instead of rewriting this workflow.

## Required Constraints

- Do not skip solution selection by default; only the local-tweak whitelist (single form field / single filter chip / single dialog content / styling-copy-props-only) may bypass it.
- Do not ask the user to "describe the style they want" in the abstract when you can provide concrete business solution options.
- Do not offer more than 4 solution options at once.
- Do not present two options that differ only by cosmetic wording; options must imply a different business structure, content surface, detail carrier, or edit mode.
- Do not default every page to a CRUD table shell; solution selection exists to prevent that failure mode.
- Do not stack the "4 KPI cards + top search + big table" backend triplet on a page without business evidence; treat it as a forbidden default.
- Do not invent dashboards, KPI cards, sidebars, or banners unless the selected solution actually requires them and the business model supports them.
- Do not present a solution option without its ASCII skeleton, edit gradient, core components, and "不借鉴清单" summary; missing fields cause drift in implementation.
- If the user has already approved a solution in the current thread, reuse it and avoid re-asking unless requirements materially changed.
- When the user references an existing page as the anchor, treat that page as a business solution source and explain the mapped solution name explicitly.
- Do not treat solution choice as component proof; after selection, implementation must still use `../jetlinks-web/SKILL.md` to verify current workspace `jetlinks-web-core` components.
- Do not offer a solution copied from a completely different business scenario unless you can explain the shared user task and what will not be borrowed.
- Do not let "frontend-design" or any other design skill override the chosen solution; Ant Design / Ant Design Vue and the catalog's hard constraints remain the visual baseline.

## Response Shape

When solution selection is needed:

1. Why solution choice matters for this page (which first-task is the user really doing)
2. Recommended solution and 1-3 alternatives, each with: business fit, first-screen ASCII skeleton, density target, edit trigger gradient, core components, state/label anchor, main action placement
3. What will not be borrowed from unrelated examples (per each option's "不借鉴清单")
4. The default you will use if the user has no objection, with a single-sentence business reason
5. Anti-admin-shell constraints that will be enforced once the user picks

When a solution is already chosen:

1. Chosen solution name
2. Stable structure, filter surface, content surface, detail carrier, edit mode, core components, action placement, density target, sidebar mode
3. Anti-admin-shell hard constraints that apply (edit gradient, no-stack first screen + one main anchor per screen, state-before-fields + no single-side colored bar, density, modal-not-only-edit-path, detail-page header summary zone with inline-edit basics, site-wide edit interaction unification, detail-page 10 hard rules + AI-flavor self-check + reverse-reference as main section when applicable, sidebar two-tier active rule + 8 collapsible-group rules + top-level root routes skip PageHead, tokenized z-index + single-FAB-per-page)
4. Which implementation skill to combine next and what `jetlinks-web-core` components still need verification
