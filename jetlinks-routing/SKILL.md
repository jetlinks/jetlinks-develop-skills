---
name: jetlinks-routing
description: Discover JetLinks workspace structure and choose the correct module or create a new one. Use when Codex needs to map the current repository, locate the right business module, understand symlinked modules, or create a new module in a low-context scaffold.
---

# JetLinks Routing

Read [`references/module-list.md`](references/module-list.md) first.

## Workflow

1. Inspect the root layout, parent `pom.xml`, aggregator modules, and symlinked directories.
2. Identify the candidate business modules and explain why each one matches the request.
3. If no existing module fits, read [`references/module-creation-rules.md`](references/module-creation-rules.md) and create the smallest compliant module structure.
4. Prefer extending an existing module before creating a new one.

## Required Constraints

- Do not hardcode module inventories into the skill output.
- Do not ignore symlinked modules or external subprojects linked into the workspace.
- Do not create a new module just because the static list is unclear.

## Response Shape

1. Workspace structure
2. Candidate modules
3. Recommended code location
4. Whether a new module is required
