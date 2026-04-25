---
name: jetlinks-web
description: 在 JetLinks 前端工作区中实现或改造 Vue3 页面，优先复用 `@jetlinks-web-core` 与 `@jetlinks-web` 的组件、hooks、utils。适用于列表页/详情页/弹窗开发、目录落点判断、状态管理、类型与质量约束、Tab 回传、平台上下文、运行时注册扩展、路由菜单装配与查询参数编码等场景。
---

# JetLinks Web

Read [`references/web-development-rules.md`](references/web-development-rules.md) first.

## Workflow

1. Read [`references/web-development-rules.md`](references/web-development-rules.md) and classify the task as page implementation, capability reuse, state/quality concerns, in-framework interaction polishing, or business-driven experience design.
2. Inspect adjacent production code and verify workspace facts (actual exports, package availability, adjacent examples, and module structure), then extract current framework style anchors such as 组件组合、间距节奏、表单/表格模式、色彩状态、弹窗/抽屉行为和动效强度。
3. Analyze the real business goal before sketching UI: target users, high-frequency tasks, key decisions, status transitions, exception paths, and whether the page is actually CRUD-heavy or should be workbench / detail / dashboard / process-oriented.
4. If core business intent, user role, or key interaction is ambiguous and the ambiguity affects page structure or interaction model, ask the user concise clarification questions before coding instead of defaulting to a generic backend CRUD layout.
5. Select only the minimal additional references from [`references/index.md`](references/index.md) based on task scope.
6. When the task includes UI or interaction optimization, combine with `$frontend-design` only after locking these local style anchors; use it to refine hierarchy, feedback, and micro-interactions inside the current framework style instead of inventing a new visual language.
7. If the page skeleton or interaction path is still uncertain, or the user would benefit from validating direction first, provide a low-fidelity wireframe or effect sketch before implementation, then code after alignment.
8. Implement the smallest complete change with Vue 3 SFC + `script setup lang="ts"` after confirming reusable abstractions.
9. Run quality and type checks with [`references/quality-and-type-rules.md`](references/quality-and-type-rules.md) before final output.
10. Pair with `$jetlinks-conventions` when naming/import/i18n consistency is needed, and with `$jetlinks-delivery` when commit or PR output is requested.

## Required Constraints

- Do not invent component props, emits, hook signatures, or utils APIs that are not present in current workspace exports.
- Do not duplicate existing `jetlinks-web-core` or `@jetlinks-web` abstractions with ad hoc local wrappers.
- Do not hardcode route auth buttons, menu metadata, API base behavior, or token handling when existing abstractions already cover them.
- Do not load every reference by default; choose only the files needed by the current scenario.
- Treat components/hooks/utils listed in references as candidates, not guaranteed facts; verify against current workspace exports before implementation.
- Prefer existing page composition patterns such as `ProSearch`, `j-pro-table`, `CardBox`, and `EditDialog` for standard management pages.
- Do not force every frontend requirement into a search-form + table + modal CRUD shell; first decide whether the business is better expressed as workspace, drill-down detail, timeline, dashboard, wizard, kanban, topology, or mixed interaction.
- When pairing with `$frontend-design`, current workspace design tokens, component library, typography, spacing scale, icon style, and motion rhythm override the skill’s default “bold aesthetic” guidance.
- Unless the user explicitly asks for a redesign, do not introduce a new brand palette, font system, page shell, or decorative style that conflicts with the current frontend framework.
- Prefer polishing existing interaction patterns such as search areas, operation bars, form grouping, cards, tabs, drawers, and loading/empty/error states instead of rebuilding the page into a self-styled showcase.
- If critical interaction decisions are under-specified, ask the user instead of guessing; if alignment is easier visually, show a wireframe or effect sketch first.
- If frontend changes cannot be fully verified in-session, state the exact pending quality or type-check commands and remaining UI risks.

## Response Shape

1. Frontend task type and target module
2. Business goal, target users, and why this is or is not a standard CRUD page
3. Current framework style anchors plus reused components/hooks/utils/capabilities and key contracts
4. If `$frontend-design` was used, which interaction or visual refinements stayed aligned with local style
5. Whether a wireframe / effect sketch was provided or why it was unnecessary
6. Main code changes and compatibility risks
7. Verification evidence or pending commands (UI interaction, state flow, route or permission behavior, and type checks)
