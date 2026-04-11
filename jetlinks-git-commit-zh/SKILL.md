---
name: jetlinks-git-commit-zh
description: Draft, refine, review, and command-wrap Chinese Conventional Commit messages. Use when a repository expects Chinese commit messages; when type, scope, body, footer, breaking-change markers, or trailers need to be chosen; when an existing commit message needs compliance review; or when a shell-specific git commit command is needed for bash, zsh, PowerShell, or cmd without broken literal \n newlines.
---

# Git Commit Zh

## Core Behavior

Return only the final commit message by default. Add explanation, alternatives,
or command wrappers only when the user asks for them.

For multi-line messages, preserve real blank lines between header, body, and
footer. Never emit placeholder text such as `// 空一行`.

## Commit Message Rules

Use one of these headers:

```text
<type>: <subject>
<type>(<scope>): <subject>
<type>!: <subject>
<type>(<scope>)!: <subject>
```

Rules:

- `Header` is required; `Body` and `Footer` are optional.
- Omit `(scope)` when it is unclear, broad, or decorative.
- Write `subject` in Chinese, describe the main change, and omit final
  punctuation.
- Add `Body` only for rationale, impact, migration notes, or trade-offs.
- Add `Footer` only for metadata such as `Refs: #123`, `Closes: #123`, or
  `BREAKING CHANGE: ...`.
- Mark breaking changes with `!` and/or `BREAKING CHANGE:` when needed.
- Keep lines within 72 characters when practical; never exceed 100.
- Follow repository-specific commit rules when they conflict with this default.

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

Choose the type that best represents the dominant change. If the repository uses
a smaller allowed type set, stay within that set.

## Output Modes

- Draft: inspect the diff, changed files, or summary; return the best message.
- Refine: preserve intent while tightening `type`, `scope`, and wording.
- Review: return `是否合规`, concrete problems, and a corrected version if needed.
- Command: if the user asks for a ready-to-run command, match the current shell.

## Shell Commands

For header-only commits, `git commit -m "<header>"` is acceptable on all
platforms.

For multi-line commits, never rely on literal `\n` inside `git commit -m`.
Read `shell-commit-examples.md` when the user wants a ready-to-run command, asks
about bash/zsh/PowerShell/cmd, or needs to fix a commit containing literal `\n`.

If the shell is unclear, return the final commit message first and note that the
exact command form depends on the shell.

## Self-Check

- The output mode matches the request.
- The message is Chinese except required tokens or trailers.
- The header format is valid and the type matches the dominant change.
- Scope is useful rather than decorative.
- Breaking changes are clearly marked.
- Ready-to-run commands use real newlines and match the user's shell.
- No explanatory prose leaks into the final commit message when the user only
  asked for the message.
