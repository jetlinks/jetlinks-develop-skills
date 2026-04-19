---
name: jetlinks-web
description: 在 JetLinks 前端工作区中实现或改造 Vue3 页面，优先复用 `@jetlinks-web-core` 与 `@jetlinks-web` 的组件、hooks、utils。适用于列表页/详情页/弹窗开发、目录落点判断、状态管理、类型与质量约束、Tab 回传、平台上下文、运行时注册扩展、路由菜单装配与查询参数编码等场景。
---

# JetLinks Web

Read [`references/web-development-rules.md`](references/web-development-rules.md) first.

## Workflow

1. Read [`references/web-development-rules.md`](references/web-development-rules.md) and classify the task as page implementation, capability reuse, or state/quality concerns.
2. Inspect adjacent production code and verify workspace facts (actual exports, package availability, adjacent examples, and module structure).
3. Select only the minimal additional references from [`references/index.md`](references/index.md) based on task scope.
4. Implement the smallest complete change with Vue 3 SFC + `script setup lang="ts"` after confirming reusable abstractions.
5. Run quality and type checks with [`references/quality-and-type-rules.md`](references/quality-and-type-rules.md) before final output.
6. Pair with `$jetlinks-conventions` when naming/import/i18n consistency is needed, and with `$jetlinks-delivery` when commit or PR output is requested.

## Required Constraints

- Do not invent component props, emits, hook signatures, or utils APIs that are not present in current workspace exports.
- Do not duplicate existing `jetlinks-web-core` or `@jetlinks-web` abstractions with ad hoc local wrappers.
- Do not hardcode route auth buttons, menu metadata, API base behavior, or token handling when existing abstractions already cover them.
- Do not load every reference by default; choose only the files needed by the current scenario.
- Treat components/hooks/utils listed in references as candidates, not guaranteed facts; verify against current workspace exports before implementation.
- Prefer existing page composition patterns such as `ProSearch`, `j-pro-table`, `CardBox`, and `EditDialog` for standard management pages.
- If frontend changes cannot be fully verified in-session, state the exact pending quality or type-check commands and remaining UI risks.

## Response Shape

1. Frontend task type and target module
2. Reused components/hooks/utils/capabilities and key contracts
3. Main code changes and compatibility risks
4. Verification evidence or pending commands (UI interaction, state flow, route or permission behavior, and type checks)
