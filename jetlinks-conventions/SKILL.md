---
name: jetlinks-conventions
description: Apply shared JetLinks coding conventions in the current workspace. Use when Codex needs to confirm annotations and imports, follow local naming and package patterns, keep changes minimal, or add i18n only when the module already uses it.
---

# JetLinks Conventions

Read [`references/code-conventions.md`](references/code-conventions.md) first.

## Workflow

1. Inspect adjacent production code before changing anything.
2. Confirm the current module's programming style, package roots, and naming patterns.
3. Use [`references/annotations-and-imports-reference.md`](references/annotations-and-imports-reference.md) when imports or annotations are unclear.
4. Use [`references/i18n.md`](references/i18n.md) only when the module already has i18n conventions or the user explicitly asks for it.
5. Implement the smallest consistent change that matches the existing codebase.

## Required Constraints

- Do not invent package names, import families, resource IDs, action IDs, topics, or service IDs.
- Do not add extra layers, helper classes, or demo code unless the task requires them.
- Prefer local examples over generic memory.
- Clearly separate workspace facts from fallback defaults when the repository is low-context.

## Response Shape

1. Conventions to follow
2. Adjacent files or patterns checked
3. Any unresolved import or i18n risks
