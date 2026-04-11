---
name: git-commit-zh
description: Use when a repository expects Chinese Conventional Commits or similar team rules, and the correct type, scope, body, footer, breaking-change marker, or trailer needs to be chosen or checked.
---

# Git Commit Zh

## Overview

Write or review Git commit messages in Chinese for repositories that use
Conventional Commits or a compatible team subset.

Prefer returning only the final commit message unless the user asks for
options or a compliance review.

## When to Use

- The user asks for a Chinese commit message.
- The user wants to check whether an existing message is compliant.
- `type`, `scope`, `body`, `footer`, or trailer usage is unclear.
- The change may need `!` or `BREAKING CHANGE:`.

## Commit Format

Use one of these headers:

```text
<type>: <subject>
<type>(<scope>): <subject>
<type>!: <subject>
<type>(<scope>)!: <subject>
```

Then optionally add:

```text
<body>

<footer trailers>
```

Apply these rules:

- `Header` is required.
- `Body` and `Footer` are optional.
- Insert one blank line between sections that are present.
- Never emit placeholder text such as `// 空一行`.
- If the user only needs a simple `git commit -m`, default to `Header` only.
- If repository rules differ from generic Conventional Commits, follow the repo.

## Type Selection

- `feat`: 新功能
- `fix`: 修复缺陷
- `docs`: 文档变更
- `style`: 代码格式调整，不影响运行结果
- `refactor`: 重构，不新增功能，也不修复缺陷
- `perf`: 性能优化
- `test`: 新增或调整测试
- `build`: 构建系统或依赖变更
- `ci`: CI 配置或流水线变更
- `chore`: 辅助工具、脚本或杂项维护
- `revert`: 回滚已有提交

When multiple types seem possible, choose the one that best describes the
dominant change.

If the repository clearly uses a smaller allowed set, stay within that set.

## Header Rules

- Omit `(scope)` when the scope is unclear, too broad, or merely decorative.
- Keep `subject` short, specific, and written in Chinese.
- Describe the main change, not the process used to make it.
- Do not end `subject` with punctuation.
- Use `!` when the change breaks compatibility or external behavior.

## Body And Footer

- Add a `Body` only when rationale, impact, or migration notes matter.
- Do not restate `Header` in the `Body`.
- Add a `Footer` only when references or metadata add value.
- Prefer standard trailers such as `Refs: #123`, `Closes: #123`, or
  `BREAKING CHANGE: ...` when applicable.
- Keep `Body` and `Footer` in Chinese unless a token must stay in English.

## Output Modes

- Drafting: default to returning only the final commit message.
- Refining: preserve intent, but tighten `type`, `scope`, and wording.
- Reviewing: return `是否合规`, then problems, then a corrected version if needed.

## Self-Check

- The output fits the user's mode: draft, refine, or review.
- The message is in Chinese, except for required tokens or trailers.
- The header format is valid.
- The selected `type` matches the dominant change.
- `scope` is useful rather than decorative.
- Breaking changes use `!` and/or `BREAKING CHANGE:` when needed.
- Keep lines within 72 characters when possible; never exceed 100.
- No placeholder text or explanatory prose leaks into the final commit message.

## Common Mistakes

- Picking `scope` just because the format allows it.
- Writing `subject` as a process description like "处理一下" or "优化代码".
- Repeating the header in the body instead of adding rationale or impact.
- Writing free-form footer prose when a trailer would be clearer.
- Forgetting to mark a breaking change.

## Examples

```text
fix(core): 修复 TopicTrie 并发可见性问题

将结构引用的 VarHandle 访问改为 volatile 语义，
避免无锁读线程读取到过期的 null。
```

```text
feat(api)!: 重命名设备批量导入接口

BREAKING CHANGE: 旧的 /devices/import/batch 路径已移除
```
