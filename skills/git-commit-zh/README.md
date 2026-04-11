# git-commit-zh

Chinese commit-message skill for repositories that use Conventional Commits or
similar team rules.

## What It Does

- Drafts Chinese commit messages.
- Refines existing commit messages.
- Reviews whether a commit message is compliant.
- Helps choose `type`, `scope`, `body`, `footer`, `!`, and standard trailers.
- Includes shell-specific examples for bash, zsh, PowerShell, and cmd.

## Files

```text
git-commit-zh/
  SKILL.md
  README.md
  shell-commit-examples.md
```

`SKILL.md` is the actual skill definition. This `README.md` is only a short
human-facing description for the repository.

## Typical Uses

- Generate a Chinese `git commit -m` message from a diff or summary.
- Check whether an existing message follows team rules.
- Rewrite a weak subject or an unnecessary scope.
- Mark breaking changes with `!` or `BREAKING CHANGE:`.
