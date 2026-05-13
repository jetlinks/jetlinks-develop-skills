---
name: jetlinks-web-style
description: 为 JetLinks 前端页面选择、复用并约束业务交互方案。这是 JetLinks 前端交互方案选择的核心入口。除非任务属于"局部调整白名单"（改一个字段 / 改一个筛选条件 / 改一个弹窗 / 仅样式与文案 props 微调），任何新增页面、重构页面壳层、调整信息架构或主筛选 / 主列表 / 主详情承载都必须先在 `style-catalog.md` 的 13 个交互方案（标准管理表格 / 资产卡片台账 / 筛选工作台 / 多对象对比 / 处置工作台 / 对象详情工作区 / 主从详情工作区 / 配置态-运行态切换 / 配置向导 / 资源选择器 / 监控感知 / 分析钻取 / 时间线日志流）中给用户 2-4 个具体业务选项再实现，并按统一字段（业务任务 / 首屏 ASCII 线框 / 信息密度 / 编辑梯度 / 核心组件 / 状态锚点 / 不借鉴清单）稳定复用结构与 `jetlinks-web-core` 组件组合，禁止默认回退成"传统后台表格 + 编辑弹窗"套壳。
---

# JetLinks Web Style

Read [`references/style-selection-rules.md`](references/style-selection-rules.md) first. Solution selection is **mandatory by default**; only the local-tweak whitelist may skip it.

## Workflow

1. Read [`references/style-selection-rules.md`](references/style-selection-rules.md) and determine whether this task hits the **local-tweak whitelist** (single form field, single filter chip, single dialog content, styling/copy/props-only). If it does, hand back to `../jetlinks-web/SKILL.md` for direct implementation. Otherwise, the rest of this workflow is mandatory.
2. If the user already named a solution, reference page, or said "按当前资产页这种结构", map it directly to the closest solution in [`references/style-catalog.md`](references/style-catalog.md) and continue.
3. Unless the task hits the local-tweak whitelist, you must present 2-4 concrete business solutions from [`references/style-catalog.md`](references/style-catalog.md) and wait for the user's choice. Do not silently default to a CRUD shell. Do not ask an open-ended design question.
4. Pick solutions using the catalog's "业务任务 → 方案路由" table; identify the user's first task on the page first, then map to 2-4 candidates from the corresponding group.
5. For each option, describe the business fit, first-screen ASCII skeleton, information density target, edit trigger gradient, core `jetlinks-web-core` components, state/label anchor, main action placement, and what should not be borrowed from unrelated pages.
6. After the user chooses, record a compact solution profile in your working notes: solution name, primary filter surface, content surface, detail carrier, edit mode, core components, action placement, density target, and sidebar mode.
7. Restate the anti-admin-shell hard constraints from [`references/style-catalog.md`](references/style-catalog.md) that apply to the chosen solution (edit trigger gradient, no-stack first screen, state-before-fields, density target, modal-is-not-the-only-edit-path), so implementation does not drift.
8. Hand implementation back to `../jetlinks-web/SKILL.md`, but keep the chosen solution profile stable unless the user explicitly changes it; component availability must still be verified from the target workspace `jetlinks-web-core`.
9. When the user says "复用现在这种风格", treat it as a request to reuse the closest business interaction solution; match the existing structure and interaction skeleton instead of inventing a visually different page shell.
10. When a new reusable solution emerges, extend [`references/style-catalog.md`](references/style-catalog.md) instead of rewriting this workflow.

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
3. Anti-admin-shell hard constraints that apply (edit gradient, no-stack first screen, state-before-fields, density, modal-not-only-edit-path)
4. Which implementation skill to combine next and what `jetlinks-web-core` components still need verification
