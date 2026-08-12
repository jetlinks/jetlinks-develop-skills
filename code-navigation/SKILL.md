---
name: code-navigation
description: 在任意语言、构建系统和代码仓库中进行环境无关的代码结构检索、符号导航、依赖与调用关系分析、执行路径追踪和变更影响定位。适用于需要查找定义 / 引用 / 实现、识别组件所有权、梳理调用方与消费者、建立最小系统图、根据变更推荐候选测试，或在上下文恢复时从精确代码锚点继续工作的场景；先发现当前环境实际提供的检索能力并按证据强度选择，不要求特定版本控制、语言服务器、索引器、数据库、MCP 或本地安装工具。
---

# Code Navigation

Read [`references/navigation-and-evidence-rules.md`](references/navigation-and-evidence-rules.md) first. Read [`references/tooling-options.md`](references/tooling-options.md) only when comparing, installing, evaluating, or replacing a retrieval backend.

## Workflow

1. State the decision question before searching: literal fact, ownership, definition / reference / implementation, hierarchy, build dependency, caller / callee, framework or domain flow, change impact, test impact, or conceptual similarity.
2. Discover the current workspace facts and available retrieval capabilities. Reuse valid user-provided paths, symbols, changed items, task anchors, indexes, and source fingerprints. Do not assume a version-control system, language, build tool, graph backend, or installed command.
3. Select the cheapest available capability that can provide sufficient evidence:
   - Exact path, literal, configuration, and source-history lookup for known facts.
   - Build or package metadata for component dependencies and ownership.
   - Compiler, language service, or semantic index for definitions, references, implementations, hierarchy, and type-aware navigation.
   - Syntax extractors or persisted structure indexes for bounded cross-file relationships and impact candidates.
   - Framework / domain extractors for registrations, messages, routes, resources, and other relations generic call graphs cannot resolve.
   - Program analysis or runtime evidence only when cheaper static evidence cannot answer the question.
4. Start from one explicit anchor and expand the minimum next relation needed for the decision. Bound nodes, paths, files, depth, output size, and uncertainty; expand again only when the result changes the next action.
5. Confirm high-impact conclusions against the strongest available source: current code, build / package metadata, compiler semantics, tests, or scoped runtime evidence. Treat stale, partial, syntactic, heuristic, and similarity-based results as candidates.
6. Return a minimal map with stable locators, relation kinds, evidence sources, source fingerprints, confidence, affected consumers, and candidate tests. Pass only these anchors to the active task, domain, recovery, or delivery workflow.

## Required Constraints

- Remain environment-neutral. Do not require or silently install a particular search command, VCS, LSP, index format, graph database, hosted service, MCP server, or runtime probe.
- Do not select a backend because it exists in the skill author's environment. Discover capabilities in the active environment and degrade cleanly when a layer is unavailable.
- Do not call every relation “dependency”. Distinguish containment, build dependency, import, reference, inheritance, call, possible dynamic target, registration, message / event flow, data access, routing, test, coverage, and historical co-change.
- Do not use textual or vector similarity as proof of an exact symbol, call, dependency, coverage, or runtime relationship.
- Do not read an entire repository or graph when exact anchors or a bounded query can answer the next decision.
- Do not stop at the failing file for complex work. Cover the smallest complete producer-boundary-transform-consumer path and the variants relevant to the hypothesis.
- Preserve uncertainty for dynamic dispatch, dependency injection, proxies, reflection, generated code, runtime registration, and constructed identifiers. Record provenance and confidence and request stronger evidence only when needed.
- Keep generated indexes, caches, visualizations, and runtime traces outside authoritative source documentation and normal version control unless the active repository explicitly defines another artifact policy.

## Response Shape

1. Retrieval question and starting anchor
2. Available capabilities and selected evidence layers
3. Minimal structure or execution path with stable locators
4. Confirmed relations versus extracted, inferred, runtime-scoped, or ambiguous relations
5. Impacted consumers and candidate tests
6. Remaining uncertainty and the cheapest next discriminating query
