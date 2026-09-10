---
name: jetlinks-routing
description: 发现 JetLinks 工作区结构并选择正确模块，必要时创建新模块。适用于需要梳理当前仓库结构、定位业务模块、识别软链接模块，或在低上下文脚手架中创建新模块的场景。
---

# JetLinks Routing

Use [`references/module-list.md`](references/module-list.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

## Workflow

1. Inspect the root layout, parent `pom.xml`, aggregator modules, and symlinked directories. When the workspace already has a valid module / symbol index, use `$code-navigation` to narrow candidate modules, then confirm ownership against the actual build manifests.
2. If the request creates a new backend module or large backend capability, first follow [`../jetlinks-router/references/backend-design-test-driven-rules.md`](../jetlinks-router/references/backend-design-test-driven-rules.md): reuse or record the task contract and relevant test goals, apply its authorization rule, and synchronize accepted durable module boundaries when needed.
3. Identify the candidate business modules and explain why each one matches the request.
4. If no existing module fits, read [`references/module-creation-rules.md`](references/module-creation-rules.md) and create the smallest compliant module structure.
5. When creating a module that includes public contracts, starter configuration, SPI registration, or first sample code, identify comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md).
6. Prefer extending an existing module before creating a new one.
7. Use [systematic-solving Admission](../systematic-solving/SKILL.md#admission) to decide whether this problem needs structured investigation. It owns hypotheses, evidence and stagnation control; this skill owns the domain implementation. A known cross-layer change or approved retry / mock is not itself an admission signal.

## Required Constraints

- Do not hardcode module inventories into the skill output.
- Do not treat imports or graph communities as Maven dependency / ownership facts; confirm the selected module in reactor and module build files.
- Do not ignore symlinked modules or external subprojects linked into the workspace.
- Do not create a new module just because the static list is unclear.
- Keep module placement or creation changes scoped to the requested capability; do not reshuffle unrelated modules or aggregators.
- When a workspace uses `manager` / `core` layering, place CRUD, controllers, application services, persistence, permissions, i18n, and runtime wiring in `manager`; keep `core` limited to shared domain objects, DTOs, commands, events, constants, SPI, and extension contracts. Do not create `xxx-api` by default.
- For a new backend module or large capability, follow [backend design](../jetlinks-router/references/backend-design-test-driven-rules.md) for the relevant module contract, test goals and unresolved decisions; reuse clear user authorization.
- Do not create public module contracts, configuration classes, SPI registration entry points, or first sample code without useful class / contract comments when they establish the module's extension boundary.
- If module or structure changes are made, report the validation performed or the exact pending commands and placement risks.

## Response Shape

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

1. Workspace structure
2. Candidate modules
3. Recommended code location
4. Task-contract path, authoritative-doc sync decision, and test goals when the backend design gate applies
5. Whether a new module is required
6. Comment targets added, or the concrete reason no code comments were needed
7. Validation notes or pending commands
