---
name: jetlinks-conventions
description: 在当前 JetLinks 工作区中应用共享编码规范。适用于需要确认注解和导入、遵循本地命名与包结构、保持最小改动，判断模块是否应该补 i18n，或实现 LocaleUtils、I18nEnumDict、messages_zh/messages_en、权限动作文案等国际化内容的场景。
---

# JetLinks Conventions

Read [`references/code-conventions.md`](references/code-conventions.md) first.

## Workflow

1. Classify the task as annotations/imports, general conventions, or i18n.
2. Inspect adjacent production code before changing anything.
3. Confirm the current module's programming style, package roots, naming patterns, and smallest-change expectation.
4. Use [`references/annotations-and-imports-reference.md`](references/annotations-and-imports-reference.md) when imports or annotations are unclear.
5. Use [`references/i18n.md`](references/i18n.md) to decide whether the module should receive i18n changes at all.
6. Use [`references/i18n-usage.md`](references/i18n-usage.md) when the task needs concrete i18n implementation details such as resource layout, `LocaleUtils`, exception `i18nCode` usage, reactive usage, `I18nEnumDict`, or resource synchronization.
7. Implement the smallest consistent change that matches the existing codebase and explicitly state the i18n decision when it matters.

## Required Constraints

- Do not invent package names, import families, resource IDs, action IDs, topics, or service IDs.
- Do not add extra layers, helper classes, or demo code unless the task requires them.
- Prefer local examples over generic memory.
- Clearly separate workspace facts from fallback defaults when the repository is low-context.
- Do not introduce i18n into a module unless the module already follows an i18n convention or the user explicitly asks for it.
- For user-visible exceptions, prefer the local exception pattern that carries `i18nCode` or message key plus args; do not hardcode Chinese or English text in exception constructors.

## Response Shape

1. Conventions to follow
2. Adjacent files or patterns checked
3. I18n decision or unresolved import/i18n risks
