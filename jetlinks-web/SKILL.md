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
4. Before coding, check five decision facts: target user, first task after entering the page, success criterion, whether the user operates one object or many, and the source of any key metric/chart. If any one is critical and unknown, ask the user first; if two or more are unknown, or page type is still undecided across multiple patterns, you must stop and clarify before implementation.
5. Select only the minimal additional references from [`references/index.md`](references/index.md) based on task scope, and treat references as supporting material only after the business model is clear.
6. When page type is unclear, load [`references/page-pattern-decision-rules.md`](references/page-pattern-decision-rules.md) first; when deciding whether a block should exist, load [`references/block-admission-rules.md`](references/block-admission-rules.md); when borrowing from examples, load [`references/business-ui-example-rules.md`](references/business-ui-example-rules.md).
7. When the task includes expression-style search, tokenized condition editing, dynamic route query encoding, remote option panels, or quick filter sidebars, load [`references/condition-filter-rules.md`](references/condition-filter-rules.md).
8. Prefer adjacent pages, same-domain modules, or similar business scenarios as references; extract interaction patterns, information architecture, and feedback rhythm, but do not copy flows, metrics, or page shells from unrelated business domains.
9. When the task includes UI or interaction optimization, combine with `$frontend-design` only after locking these local style anchors plus the Ant Design / Ant Design Vue baseline; use it to refine hierarchy, feedback, and micro-interactions inside the current framework style instead of inventing a new visual language.
10. When the user explicitly asks to follow an existing page style, or the page could reasonably be implemented in several different shells, pair with `../jetlinks-web-style/SKILL.md` first and let the user choose from a small set of concrete style options before coding.
11. If the page skeleton or interaction path is still uncertain, or the user would benefit from validating direction first, provide a low-fidelity wireframe or effect sketch before implementation, then code after alignment.
12. Implement the smallest complete change with Vue 3 SFC + `script setup lang="ts"` after confirming reusable abstractions.
13. Before final output, verify how the current workspace handles frontend i18n for user-visible copy such as 页面标题、区块标题、字段展示名、表格列头、按钮、Tab、空态、Tooltip、校验提示和枚举文案; follow adjacent code instead of scattering hardcoded strings.
14. Run quality and type checks with [`references/quality-and-type-rules.md`](references/quality-and-type-rules.md) before final output.
15. Pair with `$jetlinks-conventions` whenever naming/import/i18n consistency or user-visible copy changes are involved, and with `$jetlinks-delivery` when commit or PR output is requested.

## Required Constraints

- Do not invent component props, emits, hook signatures, or utils APIs that are not present in current workspace exports.
- Do not duplicate existing `jetlinks-web-core` or `@jetlinks-web` abstractions with ad hoc local wrappers.
- Do not hardcode route auth buttons, menu metadata, API base behavior, or token handling when existing abstractions already cover them.
- Do not load every reference by default; choose only the files needed by the current scenario.
- Treat components/hooks/utils listed in references as candidates, not guaranteed facts; verify against current workspace exports before implementation.
- Only after the page is explicitly classified as a standard management page may you prioritize patterns such as `ProSearch`, `j-pro-table`, `CardBox`, and `EditDialog`.
- Business goals come first and references come second; do not let a borrowed layout overrule the actual business task, user role, or decision path.
- Do not force every frontend requirement into a search-form + table + modal CRUD shell; first decide whether the business is better expressed as workspace, drill-down detail, timeline, dashboard, wizard, kanban, topology, or mixed interaction.
- Use Ant Design / Ant Design Vue and current workspace wrappers as the default visual and interaction language unless the user explicitly requires otherwise.
- References should come from adjacent pages, same-domain modules, or similar business scenarios; borrow only what still matches the current business semantics, and do not transplant interaction flows from completely different domains.
- When pairing with `$frontend-design`, current workspace design tokens, Ant Design component language, typography, spacing scale, icon style, and motion rhythm override the skill’s default “bold aesthetic” guidance.
- Unless the user explicitly asks for a redesign, do not introduce a new brand palette, font system, page shell, or decorative style that conflicts with the current frontend framework.
- Prefer polishing existing interaction patterns such as search areas, operation bars, form grouping, cards, tabs, drawers, and loading/empty/error states instead of rebuilding the page into a self-styled showcase.
- Do not add decorative KPI cards, fake statistics, placeholder trend charts, or any data block that has no clear business meaning, action value, or source path just to make the page look full.
- If the source path, refresh trigger, or business use of a metric/chart is unclear, do not render it.
- Do not hardcode user-visible field display names, column titles, form labels, button text, tab names, placeholders, status copy, or validation messages directly in page code; use the current workspace i18n mechanism consistently, and use Chinese as the default or fallback text only when the local abstraction supports it.
- Wireframes, effect sketches, and design reasoning are alignment artifacts for developers and stakeholders; the final implemented UI must face end users and must not expose prototype labels, interaction explanations, design principles, or development notes on the page.
- If critical interaction decisions are under-specified, ask the user instead of guessing; if alignment is easier visually, show a wireframe or effect sketch first.
- If frontend changes cannot be fully verified in-session, state the exact pending quality or type-check commands and remaining UI risks.

## Response Shape

1. Frontend task type and target module
2. Business goal, target users, and why this is or is not a standard CRUD page
3. Which references were used, why they are business-relevant, and what was deliberately not borrowed
4. Current framework style anchors plus reused components/hooks/utils/capabilities and key contracts
5. If `$frontend-design` was used, which interaction or visual refinements stayed aligned with local style and Ant Design language
6. Whether a wireframe / effect sketch was provided or why it was unnecessary
7. Main code changes and compatibility risks
8. Verification evidence or pending commands (UI interaction, state flow, route or permission behavior, and type checks)
