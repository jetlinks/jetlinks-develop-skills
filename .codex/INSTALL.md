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
ln -s ~/.codex/jetlinks-develop-skills/skills ~/.agents/skills/jetlinks-develop-skills
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\jetlinks-develop-skills" "$env:USERPROFILE\.codex\jetlinks-develop-skills\skills"
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
point `~/.agents/skills/jetlinks-develop-skills` at the repository's `skills/`
directory.

Remove any older bootstrap instructions or duplicate copied skill directories
that are no longer needed.

Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/jetlinks-develop-skills
```

You should see a symlink, or a junction on Windows, pointing to:

```text
~/.codex/jetlinks-develop-skills/skills
```

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
