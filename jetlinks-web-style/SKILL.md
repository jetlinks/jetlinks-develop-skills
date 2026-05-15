---
name: jetlinks-web-style
description: 为 JetLinks 前端页面选择、复用并约束页面风格模式。适用于任何会影响页面壳层、首屏组织、信息架构、筛选/列表/详情/工作台结构、视觉节奏或现有页面风格复用的前端页面任务；尤其是用户要求“参考当前某个页面风格”“沿用现有资产页结构”“先选页面风格再实现”，或页面可能落成标准表格页、筛选工作台式台账页、主从详情工作区、概览页、分步流、时间线、树表分组等多种结构时。与 `jetlinks-web` 配合使用，先给出少量具体风格选项或直接映射现有风格，再按已选风格稳定复用结构、信息密度和交互骨架。
---

# JetLinks Web Style

Read [`references/style-selection-rules.md`](references/style-selection-rules.md) first for page-shell selection, and read [`references/style-rules.md`](references/style-rules.md) whenever implementing visual details.

## Workflow

1. Read [`references/style-selection-rules.md`](references/style-selection-rules.md) and decide whether this task needs an explicit style choice. If the task does not affect page shell, information architecture, or visual rhythm, hand it back to `../jetlinks-web/SKILL.md` without forcing style selection.
2. If the user already named a style, a reference page, or said “按当前资产页这种结构”, map it directly to the closest catalog style and continue.
3. If multiple page shells are plausible and the choice will materially change information architecture, offer 2-4 concrete style options with a recommended default, then wait for the user's choice before implementation. Do not ask an open-ended design question.
4. Read [`references/style-catalog.md`](references/style-catalog.md) and select only the small subset of styles relevant to the current task.
5. For visual implementation details, read [`references/style-rules.md`](references/style-rules.md) and use Ant Design Vue plus `jetlinks-web-core/src/style.css` variables before local styles.
6. After the user chooses, record a compact style profile in your working notes: page style name, primary filter surface, content surface, action placement, density target, and whether a sidebar exists.
7. Hand implementation back to `../jetlinks-web/SKILL.md` or combine with it directly, but keep the chosen style profile stable unless the user explicitly changes it.
8. When the user says “复用现在这种风格”, prefer matching the existing structure and interaction skeleton over inventing a visually different page shell.
9. When a new reusable style emerges, extend `references/style-catalog.md` instead of rewriting this workflow.

## Required Constraints

- Do not ask the user to “describe the style they want” in the abstract when you can provide concrete options.
- Do not offer more than 4 style options at once.
- Do not present two options that differ only by cosmetic wording; options must imply a different structure or interaction model.
- Do not default every page to a CRUD table shell; style selection exists to prevent that failure mode.
- Do not invent dashboards, KPI cards, or sidebars unless the selected style actually requires them and the business model supports them.
- If the user has already approved a style in the current thread, reuse it and avoid re-asking unless requirements materially changed.
- When the user references an existing page as the style anchor, treat that page as the first-class style source and explain the mapped style name explicitly.
- For colors, radius, shadow, font size, spacing, card gaps, and title/subtitle rhythm, follow `references/style-rules.md`; do not fall back to ad hoc values.

## Response Shape

When style selection is needed:

1. Why style choice matters for this page
2. Recommended style and 1-3 alternatives
3. Structural difference between options
4. The default you will use if the user has no objection

When a style is already chosen:

1. Chosen style name
2. The stable structure you will reuse
3. Which implementation skill to combine next

When style selection is not needed:

1. Why the current shell can stay unchanged
2. Which implementation skill to combine next
