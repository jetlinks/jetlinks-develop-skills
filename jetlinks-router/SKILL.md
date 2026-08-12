---
name: jetlinks-router
description: 将 JetLinks 开发请求路由到当前工作区中最合适的 focused skill。适用于尚不确定应使用哪个 JetLinks 技能，或任务同时涉及复杂高难度问题的系统性求解、代码结构与依赖检索、模块落点、通用编码规范、响应式实践、CRUD、跨边界调用、事件与订阅流程、前端页面改造以及交付准备的场景。
---

# JetLinks Router

Read [`ai-prompt.md`](references/ai-prompt.md) first. Treat it as the routing index.

## Workflow

1. Classify the task.
2. Decide whether the task must enter a plan-first gate. Use it for complex, cross-module, multi-subtask, or still-changing requirements.
3. For a complex or high-uncertainty task, or whenever an attempted fix still fails / moves the failure / requires another special branch, load the generic [`../systematic-solving/SKILL.md`](../systematic-solving/SKILL.md) plus [`references/systematic-solving-jetlinks-rules.md`](references/systematic-solving-jetlinks-rules.md). Establish the task contract, competing hypotheses, local-patch budget, solution level, and validation matrix before further implementation, then map them to JetLinks artifacts and delivery rules.
4. For large backend changes or new backend features, read [`references/backend-design-test-driven-rules.md`](references/backend-design-test-driven-rules.md) and [`references/document-placement-rules.md`](references/document-placement-rules.md). When `.trellis/` exists also read [`references/trellis-integration-rules.md`](references/trellis-integration-rules.md). Draft the task contract in Trellis or one Git-ignored runtime artifact, wait for explicit confirmation, and only then promote accepted durable decisions into authoritative docs by rewriting their current state in place.
5. When plan-first is required but the backend design gate does not apply, output a concise plan that covers goal, scope, non-goals, steps, risks or pending confirmations, and validation, then wait for user confirmation before implementation.
6. For long-running work, plan-state maintenance, evidence reuse, versioned stage delivery, or after context compaction / resume / handoff, load [`../task-continuity/SKILL.md`](../task-continuity/SKILL.md) plus [`references/context-recovery-rules.md`](references/context-recovery-rules.md). Use the generic continuity protocol first, then map it to Trellis and Git facts; do not restart workspace discovery unless the saved identity or anchors conflict.
7. When ownership, callers / consumers, domain flows, or change impact are not already bounded by valid anchors, load [`../code-navigation/SKILL.md`](../code-navigation/SKILL.md). For JetLinks-specific Command / Event / Topic / AssetsHolder / protocol / frontend relations, also read [`references/code-navigation-jetlinks-rules.md`](references/code-navigation-jetlinks-rules.md). Pass only confirmed anchors and uncertain relations onward.
8. Switch to the most relevant domain-focused JetLinks skill.
9. Combine multiple focused skills when the task crosses boundaries.
10. Read adjacent production code before changing anything, except when a valid Recovery Capsule or confirmed code-navigation result already narrows the next step to verified anchors.
11. Implement complete changes, not pseudo-code.
12. Verify the final solution against the focused skills you used, and when code changes are involved run the relevant validation or state the exact pending command and residual risk.
13. If the finished task produced reusable knowledge, route to `jetlinks-capture`, give the recommendation first, and only write the document after user confirmation.
14. If the captured result is generic enough to become a shared JetLinks skill, ask whether to merge it into `jetlinks-develop-skills` and prepare an upstream PR.

## Routing

- Protocol package registration, transport codecs, and binary packet handling: [`../jetlinks-protocol/SKILL.md`](../jetlinks-protocol/SKILL.md)
- Complex, high-uncertainty, cross-boundary, or repeatedly failing tasks that need problem-model reconstruction and stagnation control: [`../systematic-solving/SKILL.md`](../systematic-solving/SKILL.md) plus [`references/systematic-solving-jetlinks-rules.md`](references/systematic-solving-jetlinks-rules.md)
- Long-running plans, non-ledger runtime state, context compaction / resume, evidence reuse, validated stage checkpoints, and task-level remote delivery: [`../task-continuity/SKILL.md`](../task-continuity/SKILL.md) plus [`references/context-recovery-rules.md`](references/context-recovery-rules.md)
- Environment-neutral code structure retrieval, exact symbol navigation, dependency / call relations, change impact, and candidate-test discovery: [`../code-navigation/SKILL.md`](../code-navigation/SKILL.md); add [`references/code-navigation-jetlinks-rules.md`](references/code-navigation-jetlinks-rules.md) only for JetLinks domain relations
- Shared coding conventions, comments, imports, i18n habits, tracing, and MBean observability: [`../jetlinks-conventions/SKILL.md`](../jetlinks-conventions/SKILL.md)
- Reactive and non-blocking implementation practice: [`../jetlinks-reactive/SKILL.md`](../jetlinks-reactive/SKILL.md)
- Workspace discovery, module placement, and module creation: [`../jetlinks-routing/SKILL.md`](../jetlinks-routing/SKILL.md)
- Standard or advanced CRUD work: [`../jetlinks-crud/SKILL.md`](../jetlinks-crud/SKILL.md)
- AssetsHolder data permission control for CRUD, custom queries, commands, subscriptions, related assets, and aggregate queries: [`../jetlinks-assets-permission/SKILL.md`](../jetlinks-assets-permission/SKILL.md)
- Direct dependency, command service, or proxy boundaries: [`../jetlinks-boundary/SKILL.md`](../jetlinks-boundary/SKILL.md)
- Domain events, lifecycle events, and real-time subscriptions: [`../jetlinks-events/SKILL.md`](../jetlinks-events/SKILL.md)
- Frontend page implementation, capability reuse, and quality constraints in JetLinks Web: [`../jetlinks-web/SKILL.md`](../jetlinks-web/SKILL.md). First analyze the real business workflow instead of defaulting to backend CRUD. Treat references as supporting material from adjacent pages or similar business scenarios, keep Ant Design as the baseline style, avoid meaningless decorative data, and make sure prototype annotations stay out of the final user-facing UI. Backend `EnumDict` / `I18nEnumDict` fields usually render as `{ value, text }`: display `text`, submit/filter by `value`. Except for the `jetlinks-web-style` local-tweak whitelist, route frontend page implementation through `../jetlinks-web-style/SKILL.md` together with `../jetlinks-web/SKILL.md` before coding so a solution profile is locked first.
- Frontend page style selection and structural reuse: [`../jetlinks-web-style/SKILL.md`](../jetlinks-web-style/SKILL.md). Use it for any frontend page task that creates a page, rewrites a shell, changes first-screen organization, information architecture, main filter/list/detail carrier, visual rhythm, or structural reuse; not only when the user explicitly says “风格”. Also use it when the user wants to follow an existing page style, when a page could reasonably be built in several different shells, or when style choice should be confirmed before implementation. Standard table pages are not the fallback for missing facts, and `ProSearch` needs an explicit old-page / lightweight-filter exception reason.
- Knowledge capture and reusable summary output: [`../jetlinks-capture/SKILL.md`](../jetlinks-capture/SKILL.md)
- Branch strategy, commit titles, tests, and PR text: [`../jetlinks-delivery/SKILL.md`](../jetlinks-delivery/SKILL.md)

## Required Constraints

- Do not assume fixed module names, package roots, versions, or resource paths.
- Do not ignore symlinked modules or linked external subprojects when discovering the workspace.
- Prefer local examples over generic memory.
- Use [`../code-navigation/SKILL.md`](../code-navigation/SKILL.md) for bounded structure retrieval when exact anchors are not already known. Discover the active environment's capabilities instead of assuming Git, a search command, language server, index, graph database, or MCP. Load the JetLinks extension only when its domain relations apply.
- When local examples are missing, clearly separate defaults from verified workspace facts.
- Do not directly implement complex or unstable requirements before clarifying scope, exclusions, risks, and validation with the user.
- Do not treat plan-first as sufficient protection against iterative patching. For complex tasks, establish falsifiable hypotheses and a validation matrix through `$systematic-solving`; after one failed implementation under the same root-cause hypothesis, stop adding local branches or fallbacks and rebuild the problem model before editing again.
- Treat any new scenario-specific condition, fallback, retry, mock, compatibility alias, hidden switch, copied implementation, failure migration to a sibling scenario, or repeated action without new discriminating evidence as a stagnation signal. Route through `$systematic-solving` plus the JetLinks extension even when the task originally appeared small.
- Do not implement large backend changes or new backend features before a task contract and test goals have been recorded in the workspace's task artifact and explicitly confirmed by the user.
- Treat authoritative docs as the current accepted state, not drafts or execution logs. Rewrite stale requirements and decisions in place; do not append progress checkboxes, scan notes, debug attempts, raw test output, PR text, completion summaries, or timelines.
- Keep live plans, hypothesis ledgers, attempts, failures, next actions, and stage summaries in Trellis when present. Without Trellis or an existing task system, use one repository-local runtime file verified as ignored by Git; do not default to a committable task / worklog document or modify shared `.gitignore` merely for agent state.
- Use `$task-continuity` for plan compression, evidence reuse, context recovery, and stage / review lifecycle. Before expected compaction, pause, or handoff, and after each validated stage commit, refresh the JetLinks Recovery Capsule; on resume, verify task ID / revision, branch / HEAD, and changed paths, then read only its 3–7 anchors.
- Do not place task logs, test reports, PR descriptions, or temporary design notes into README files; README is for durable repository or module overview.
- Do not treat tests as a checkbox: test goals must map to realistic business scenarios and data, and failures must drive root-cause analysis rather than weaker assertions.
- For code changes, apply the comment gate from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md) before implementation: identify required comment targets, add comments in the touched code when complex business intent / permission boundary / compatibility / lifecycle / public contract exists, and only report "no comments needed" when the touched code is straightforward. A final summary or PR description does not replace code comments.
- For complex SQL, native SQL, aggregation, joins, deep pagination, or batch writes, prefer standard SQL and existing QueryHelper / DSL abstractions. Only accept database-specific dialect SQL when the user explicitly requires that database or the module is already database-specific; document dialect risk and require pressure testing or equivalent performance evidence.
- For critical backend business flows, state the TraceHolder tracing decision in the design or implementation summary: manual spans added, existing platform tracing coverage, or not applicable. Route detailed rules to [`../jetlinks-conventions/references/tracing.md`](../jetlinks-conventions/references/tracing.md).
- For long-lived in-memory tasks, caches, queues, buffers, retry pools, and session / connection / subscription managers, state the MBean observability decision in the design or implementation summary: MBean added, existing MBean / monitor covered, or not applicable. Route detailed rules to [`../jetlinks-conventions/references/mbean-observability.md`](../jetlinks-conventions/references/mbean-observability.md).
- Treat compatibility as a general release-boundary decision, not a CRUD-only concern. For any API, DTO, Command, Event, Topic, protocol payload, config, persisted data, frontend route parameter, QueryParam, or `termType`, collapse unreleased same-PR intermediate forms into the final best-practice design; only keep compatibility or migration for released, persisted, or externally depended-on behavior.
- Before adding compatibility code, identify the concrete compatibility target. If the only target is an earlier commit, draft, test expectation, or caller inside the same unreleased PR, do not add fallback branches, deprecated aliases, dual DTO parsing, transitional flags, migration code, or old-behavior tests; update all in-PR callers, tests, and docs to the final canonical behavior instead.
- If release or external dependency status is unknown, ask the user one direct question about whether the old behavior has been released, persisted, or externally depended on; do not invent compatibility "just in case".
- When the framework, SDK, third-party library, or existing API does not directly satisfy the requirement (inaccessible method, serialization error, reactive/blocking mismatch, type/generic clash, exception model gap, third-party behavior mismatch), route through `$jetlinks-conventions` and resolve the root cause via official extension points, adjacent module abstractions, dependency choice, or by informing the user with concrete trade-offs; never ship reflection / `Unsafe` / visibility bypass / copied source / monkey patches / bytecode injection / silent exception swallowing as a hidden workaround. See [`../jetlinks-conventions/references/root-cause-and-no-hack-rules.md`](../jetlinks-conventions/references/root-cause-and-no-hack-rules.md).
- When a scenario-specific bug points at a shared/general capability, route through `$jetlinks-conventions`; require a common root-cause fix or an explicitly modeled strategy/configuration instead of hardcoded special branches.
- When Apache Commons utilities are already present or adjacent code already uses them, prefer them for object, collection, map, and array checks. Do not route this as a blanket ban on `org.apache.commons.lang3.StringUtils`; route deprecated string comparison/search/prefix/suffix/plain replace calls through `$jetlinks-conventions` to use `Strings.CS` / `Strings.CI`, while allowing non-deprecated null-safe predicates such as `StringUtils.isEmpty` / `isBlank` when they match local Commons Lang style.
- Keep changes scoped to the requested capability; avoid unrelated refactors or speculative cleanup.
- If the tool supports a dedicated Plan mode, prefer it for plan-first tasks; otherwise still follow the same behavior manually.
- Prefer existing framework abstractions and focused skills over adding new ad hoc guidance here.

## Response Shape

When analyzing first:

1. Task classification
2. Whether plan-first confirmation is required
3. Whether backend design-test gate applies, plus the task-contract/runtime artifact and any authoritative doc that needs promotion
4. Focused JetLinks skill or skills to use
5. Systematic-solving trigger, current hypotheses, and local-patch budget when applicable
6. Code-navigation question, confirmed anchors, inferred edges, and remaining uncertainty when structure retrieval applies
7. Workspace facts to confirm
8. Proposed code and document locations
9. Release-boundary decision when compatibility is in question
10. Comment decision when complex or non-obvious code is involved
11. Database portability and performance test decision when SQL is involved
12. TraceHolder tracing decision when critical backend flows are involved
13. MBean observability decision when long-lived in-memory or cache behavior is involved
14. Plan summary, test goals, or direct-execution rationale

When implementing:

1. Quietly classify and inspect
2. If backend design-test gate applies, write or update the task contract and test goals in Trellis or the chosen Git-ignored runtime artifact, then wait for user confirmation; only accepted durable changes update authoritative docs
3. If plan-first applies without backend design gate, output the plan and wait for confirmation
4. If systematic solving applies, build the evidence-backed problem model and validation matrix before production edits; if stagnation occurs later, stop and rebuild it
5. On resume, let `$task-continuity` recover and validate the bounded route; when another relation is needed, continue from capsule symbol / flow anchors instead of scanning the repository again
6. Use `$code-navigation` to establish the smallest confirmed producer-boundary-consumer map when the route still lacks ownership, consumers, variants, or test impact; add the JetLinks domain extension only for relevant framework relations
7. Edit the code with the smallest complete change that restores the demonstrated invariant
8. Run validation at the coherent stage boundary; when it passes, create one local stage commit and then refresh the Recovery Capsule with its actual hash and the next route
9. Push and create or update the PR only after the entire task meets its acceptance matrix; do not use PR updates as per-step progress records
10. Summarize what changed, which focused skills were used, what was verified, whether knowledge capture is recommended, and whether it is worth promoting into the official skills repository
