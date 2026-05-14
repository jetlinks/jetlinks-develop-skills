---
name: jetlinks-conventions
description: 在当前 JetLinks 工作区中应用共享编码规范。适用于需要确认注解和导入、遵循本地命名与包结构、保持最小改动，判断模块是否应该补 i18n，或实现 LocaleUtils、I18nEnumDict、messages_zh/messages_en、权限动作文案等国际化内容的场景。
---

# JetLinks Conventions

Read [`references/code-conventions.md`](references/code-conventions.md) first.

## Workflow

1. Classify the task as annotations/imports, general conventions, i18n, or a capability-gap / hack-avoidance situation (tool, SDK, framework API not directly satisfying the requirement).
2. Inspect adjacent production code before changing anything.
3. Confirm the current module's programming style, package roots, naming patterns, and smallest-change expectation.
4. Use [`references/annotations-and-imports-reference.md`](references/annotations-and-imports-reference.md) when imports or annotations are unclear.
5. Use [`references/i18n.md`](references/i18n.md) to decide whether the module should receive i18n changes at all.
6. Use [`references/i18n-usage.md`](references/i18n-usage.md) when the task needs concrete i18n implementation details such as resource layout, `LocaleUtils`, exception `i18nCode` usage, reactive usage, `I18nEnumDict`, or resource synchronization.
7. Whenever an existing tool, SDK, framework API, library, or local capability does not directly satisfy the requirement (inaccessible method, serialization error, reactive/blocking mismatch, type/generic clash, exception model gap, third-party behavior mismatch, etc.), load [`references/root-cause-and-no-hack-rules.md`](references/root-cause-and-no-hack-rules.md) and resolve the root cause through official extension points, adjacent module abstractions, dependency choice, or by informing the user; never ship reflection / `Unsafe` / visibility hacks / copied source / bytecode injection / monkey patches as a silent workaround.
8. Implement the smallest consistent change that matches the existing codebase and explicitly state the i18n decision when it matters.

## Required Constraints

- Do not invent package names, import families, resource IDs, action IDs, topics, or service IDs.
- Do not add extra layers, helper classes, or demo code unless the task requires them.
- Prefer local examples over generic memory.
- Clearly separate workspace facts from fallback defaults when the repository is low-context.
- Do not introduce i18n into a module unless the module already follows an i18n convention or the user explicitly asks for it.
- When Apache Commons utilities are already available or aligned with adjacent code, prefer them for null or empty checks and common object or collection operations instead of handwritten repetitive branches.
- Keep convention-driven changes scoped to the required consistency fix; do not expand into unrelated cleanup.
- When convention-related code changes are made, report the validation performed or the exact pending commands and unresolved convention risks.
- For user-visible exceptions, prefer the local exception pattern that carries `i18nCode` or message key plus args; do not hardcode Chinese or English text in exception constructors.
- When the framework, SDK, third-party library, or existing API does not directly satisfy the requirement, solve the root cause via official extension points, adjacent module abstractions, dependency adjustments, or by informing the user with concrete trade-offs; do not use reflection / `Unsafe` / visibility bypass / copied source / monkey patches / bytecode injection / hidden access-level changes as a silent workaround. If such an option is the only path, explain the limitation and obtain user confirmation before applying it. See [`references/root-cause-and-no-hack-rules.md`](references/root-cause-and-no-hack-rules.md).
- Do not silence build / lint / type-check errors with broad `@SuppressWarnings`, commented-out code, ignored tests, swallowed exceptions (`catch (Exception e) {}`), or `e.printStackTrace()` instead of structured handling; fix the underlying issue or escalate to the user.
- Do not block in reactive modules to "make it work" or invent parallel `ObjectMapper` / serializer instances to dodge serialization errors; resolve via `Module` / `Mixin` / `JsonSerializer` / `JsonDeserializer` / `@JsonTypeInfo` and reuse the module's standard configuration.

## Response Shape

1. Conventions to follow
2. Adjacent files or patterns checked
3. I18n decision or unresolved import/i18n risks
4. If a tool/API capability gap was hit, the root cause analysis, the chosen resolution path (official extension point / adjacent abstraction / dependency change / informing the user), and any usage of reflection / visibility bypass / copied source that was explicitly confirmed by the user
5. Verification evidence or exact pending commands
