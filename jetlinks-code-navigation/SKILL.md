---
name: jetlinks-code-navigation
description: 在 JetLinks Java/Maven 与 Vue/TypeScript 工作区中进行代码结构检索、符号导航、依赖与调用链分析、领域流程追踪和变更影响定位。适用于需要快速找到定义 / 引用 / 实现、梳理模块依赖、Controller-Service-Repository 链路、Command / Event / Topic / AssetsHolder / Protocol / Vue route-API 关系、为复杂任务建立最小系统图、在上下文恢复时定向加载锚点，或根据 changed paths 推荐受影响消费者和测试的场景；不要用向量相似度替代精确符号、构建依赖和 Git 事实。
---

# JetLinks Code Navigation

Read [`references/retrieval-and-graph-rules.md`](references/retrieval-and-graph-rules.md) first. Read [`references/tooling-and-research.md`](references/tooling-and-research.md) only when designing, installing, evaluating, or replacing the retrieval backend.

## Workflow

1. State the question before searching: exact text / config, symbol ownership, callers / callees, type hierarchy, module dependency, JetLinks domain flow, change impact, test impact, or conceptual documentation.
2. Establish the current revision with lightweight Git facts and check whether a graph / symbol index exists and matches the repository root and current tree. Treat a stale or partial index as a hint, not as authority.
3. Use the cheapest sufficient retrieval layer:
   - `rg`, `rg --files`, Git, build manifests, and known exact anchors for literal facts.
   - JDT LS for Java and TypeScript language service / Vue language tools for definition, references, implementations, hierarchy, and type-aware navigation.
   - A persisted structural graph such as `code-review-graph` or SCIP for bounded multi-hop navigation, cross-file context, flows, and impact candidates.
   - JetLinks-aware AST extractors for framework and domain edges that generic call graphs cannot express reliably.
   - CodeQL / Joern or runtime traces only for data-flow, taint, dynamic dispatch, reflection, or other questions the cheaper layers cannot answer.
4. Start from one entry or changed path and expand one hop at a time. Return file / symbol anchors, relation kind, evidence source, revision, and confidence; request another hop only when it changes the decision.
5. Confirm graph-derived conclusions against source, build configuration, tests, or runtime evidence before modifying a public contract, deleting code, changing a boundary, or declaring impact complete.
6. Feed only the minimal confirmed map into `$jetlinks-systematic-solving`, the relevant domain skill, the Recovery Capsule, or `$jetlinks-delivery`. Do not paste the whole graph or a large semantic-search result into context.

## Required Constraints

- Do not call every relation “dependency”. Distinguish containment, build dependency, import, reference, inheritance, static call, possible dynamic target, framework registration, event / topic flow, data access, route, test, coverage, and Git co-change.
- Do not treat Tree-sitter extraction, simple name matching, semantic similarity, or inferred framework wiring as compiler-resolved truth.
- Do not use a repository-wide scan when exact symbols, changed paths, Recovery Capsule anchors, or a bounded graph query already identify the next decision surface.
- Do not stop at the failing file for complex work. Cover the smallest complete producer-boundary-transform-consumer path and its relevant variants.
- Do not start with an unbounded whole-repository dependency visualization. Prefer 1–2 hop queries, a concrete path trace, or change-impact slices with explicit node / token limits.
- Do not make Neo4j, embeddings, CodeQL, Joern, or a hosted code-search platform mandatory for the first implementation. Adopt them only after measured queries require their capabilities.
- Preserve uncertainty. Dynamic dispatch, proxies, reflection, Spring wiring, runtime component registration, and topic construction must carry provenance and confidence and may require runtime confirmation.
- Keep indexes, SQLite databases, generated visualizations, caches, and runtime traces out of authoritative docs and normal Git history unless the repository explicitly defines a durable generated-artifact policy.

## Response Shape

1. Retrieval question and starting anchor
2. Layers and tools used
3. Minimal structure / execution path with file and symbol anchors
4. Confirmed relations versus inferred or ambiguous relations
5. Impacted consumers and candidate tests
6. Remaining uncertainty and the cheapest next discriminating query
