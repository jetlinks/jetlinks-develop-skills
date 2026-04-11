---
name: jetlinks-i18n
description: Implement or review JetLinks internationalization as an independent skill. Use when code needs user-facing text localization, messages_zh.properties or messages_en.properties updates, LocaleUtils usage, I18nEnumDict enum keys, permission or action localization, error or prompt localization, or a decision about whether a module should introduce i18n at all.
---

# JetLinks I18n

## Core Rule

Add i18n only after confirming the target module already uses an i18n convention,
or after the user explicitly asks to introduce one. Do not create new resource
paths for formal completeness.

## Workflow

1. Inspect the target module and neighboring modules for
   `src/main/resources/i18n/...`, `messages_zh.properties`, and
   `messages_en.properties`.
2. Confirm the existing key style, language-file set, and Chinese encoding style
   before editing.
3. Add or update only user-visible text: enum labels, permission/action names,
   validation messages, errors, prompts, alarms, or status text.
4. Use `LocaleUtils.resolveMessage(...)` with a default value unless the local
   codebase uses a more specific wrapper or overload.
5. For reactive code, follow the module's existing reactive i18n pattern before
   introducing `resolveMessageReactive(...)`.
6. For `I18nEnumDict`, use keys in the form
   `{fully.qualified.EnumClass}.{ENUM_VALUE}`.
7. Keep Chinese and English files aligned when the module already maintains both.
8. Verify key spelling, default messages, resource placement, and whether the
   new text is truly user-visible.

## Reference

Open `usage-guide.md` when the task needs examples for resource layout, key
patterns, `LocaleUtils`, reactive usage, enum localization, or validation.

## Guardrails

- Do not localize internal debug-only logs.
- Do not hand-pass `LocaleUtils.current()` into `resolveMessage(...)` unless the
  local code already uses that overload for a reason.
- Do not mix UTF-8 Chinese and `\uXXXX` escaping in the same module unless the
  existing files already do so.
- Do not invent permission IDs, action IDs, enum class names, or module names.
- Do not update only one language file when the module maintains both Chinese and
  English resources.

## Self-Check

- The module convention was inspected before adding i18n.
- Resource paths and file names match the local module.
- Keys match code identifiers, permission IDs, action IDs, enum values, or error
  codes.
- Default messages are present in code where needed.
- Multi-language resources stay synchronized with the module's existing practice.
