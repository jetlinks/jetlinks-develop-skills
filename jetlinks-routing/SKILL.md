---
name: jetlinks-routing
description: 发现 JetLinks 工作区结构并选择正确模块，必要时创建新模块。适用于需要梳理当前仓库结构、定位业务模块、识别软链接模块，或在低上下文脚手架中创建新模块的场景。
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
- Keep module placement or creation changes scoped to the requested capability; do not reshuffle unrelated modules or aggregators.
- If module or structure changes are made, report the validation performed or the exact pending commands and placement risks.

## Response Shape

1. Workspace structure
2. Candidate modules
3. Recommended code location
4. Whether a new module is required
5. Validation notes or pending commands
