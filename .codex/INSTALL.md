# Installing JetLinks Develop Skills for Codex

Enable JetLinks development skills in Codex via native skill discovery. Clone
the repository and create a skills symlink.

## Prerequisites

- Git

## Installation

Clone the repository:

```bash
git clone https://github.com/jetlinks/jetlinks-develop-skills.git ~/.codex/jetlinks-develop-skills
```

Create the skills symlink:

```bash
mkdir -p ~/.agents/skills
ln -s ~/.codex/jetlinks-develop-skills ~/.agents/skills/jetlinks-develop-skills
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\jetlinks-develop-skills" "$env:USERPROFILE\.codex\jetlinks-develop-skills"
```

Restart Codex after installation so it can discover the skills.

## Migrating From Older Setups

If you previously installed this repository with a manual copy, an older
bootstrap flow, or a different link target:

Update the repository:

```bash
cd ~/.codex/jetlinks-develop-skills && git pull
```

Recreate the skills symlink using the commands above. Native discovery should
point `~/.agents/skills/jetlinks-develop-skills` at the repository root.

Remove any older bootstrap instructions or duplicate copied skill directories
that are no longer needed.

Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/jetlinks-develop-skills
```

You should see a symlink, or a junction on Windows, pointing to:

```text
~/.codex/jetlinks-develop-skills
```

This proves skill discovery only. For the optional subagent adapter, also make
the exact Codex runtime that hosts the session fully parse its configuration
and confirm that multi-Agent support is effective. For a CLI that provides the
command, use:

```bash
codex features list
```

`codex --version` is not a configuration check. A desktop app or IDE may use a
bundled runtime different from the shell's first `codex` on `PATH`, so validate
each client independently. Finally run one bounded forward test whose selected
route is not `SINGLE_OWNER`; success requires an accepted spawn receipt,
terminal Agent results, and one integrated response. Printed role prompts alone
do not prove the adapter works.

## Optional context continuity backend

The core `task-continuity` skill does not require or silently install a state
backend. If you want Codex to persist session events and restore an indexed
resume snapshot around compaction, `context-mode` already provides a Codex
plugin with `PreCompact`, `SessionStart`, SQLite, and FTS5:

```bash
codex plugin marketplace add mksglu/context-mode
codex plugin add context-mode@context-mode
```

Before installation, review its Elastic License 2.0 terms, Node.js/native
dependency requirements, local data location, and tool-routing hooks. After
installation, use `/hooks` to review and trust the exact hook definitions.
Current runtimes expose `hooks` as a stable feature and may report the older
`plugin_hooks` flag as removed; use `codex features list` for the runtime that
actually hosts the session instead of copying stale feature flags.

`ctx stats` proves only that the MCP server is reachable. Verify continuity by
running one bounded automatic or manual compaction test: `PreCompact` must
persist events, `SessionStart(source=compact)` must restore the same task, and
the first resumed productive action must hit the saved `first_allowed_action`
without a full thread or workspace reread. Keep composite source identity,
reference cursors, evidence freshness, and execution gates in
`task-continuity`; the third-party event snapshot is a backend, not the
authoritative task contract.

## Updating

```bash
cd ~/.codex/jetlinks-develop-skills && git pull
```

Skills update through the symlink after the repository changes.

## Uninstalling

```bash
rm ~/.agents/skills/jetlinks-develop-skills
```

Optionally delete the clone:

```bash
rm -rf ~/.codex/jetlinks-develop-skills
```
