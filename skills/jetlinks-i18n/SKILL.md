---
name: jetlinks-i18n
description: Use when JetLinks code needs user-facing text, properties-based localization, LocaleUtils, I18nEnumDict enums, messages_zh/messages_en files, or module-level decisions about whether i18n should be added at all.
---

# JetLinks I18n

## Overview

Handle JetLinks internationalization for user-visible text, enum text,
permissions, actions, errors, and prompts.

First confirm the target module already uses i18n conventions, or that the user
explicitly wants them. Then follow the module's existing resource layout, key
patterns, and encoding style.

## When to Use

- Adding or updating `src/main/resources/i18n/...`
- Creating `messages_zh.properties` or `messages_en.properties`
- Using `LocaleUtils.resolveMessage(...)` or reactive i18n helpers
- Localizing enums, permissions, actions, errors, or prompts
- Deciding whether a JetLinks module should introduce i18n at all

## Workflow

1. Confirm whether the target module already uses i18n.
2. Inspect neighboring modules for directory layout, key conventions, and file
   encoding style.
3. Add or update only user-visible text.
4. Keep Chinese and English resources in sync when the module maintains both.
5. Match the code style for `LocaleUtils`, `I18nEnumDict`, and exceptions.
6. Verify keys, defaults, and resource placement before finishing.

## Quick Rules

- Do not invent a new i18n layout just for completeness.
- Always provide a sensible default message in code.
- Do not localize internal debug-only logs.
- For enum i18n, keys must match the enum's fully qualified class name and value.
- For step-by-step implementation, open `usage-guide.md`.

## Common Mistakes

- Adding i18n without checking module conventions first
- Writing keys that do not match code identifiers or enum names
- Updating only one language file when the module already maintains both
- Passing `LocaleUtils.current()` into `resolveMessage(...)` unnecessarily
- Translating internal logs instead of user-facing text

## Self-Check

- The module really uses i18n already, or the user explicitly asked for it.
- Resource files are placed under the module's existing i18n path.
- Keys match code identifiers, permission IDs, action IDs, or enum values.
- Default messages are present where needed.
- Multi-language files stay aligned with local conventions.
