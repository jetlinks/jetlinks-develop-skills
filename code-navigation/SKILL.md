---
name: code-navigation
description: 从精确文件或符号查找定义、调用方、所有者、执行路径和变更影响。按证据逐步扩大检索，适配当前语言和工具；已有明确锚点的普通查询不需要任务恢复或持久索引。
---

# Code Navigation

Start with the user's decision question and existing anchor. A new task such as “find callers of this method” is a bounded query, not a recovery event; do not load continuity, construct a capsule or fingerprint the whole workspace for it.

## Retrieval

1. Reuse supplied files, symbols, changed items and still-valid source anchors. Discover only the retrieval capability needed now: exact search for literals, build manifests for ownership, semantic navigation for definitions/callers, or a bounded runtime observation for behavior static evidence cannot decide.
2. Expand from the anchor only while a relation can change the answer. Distinguish imports, build dependencies, calls, possible dynamic targets and event/registration flows. Treat syntactic, inferred and similarity matches as candidates, not proof of resolved behavior.
3. Check high-impact conclusions against current source, build facts or scoped runtime evidence. Preserve uncertainty for reflection, dynamic dispatch, injection and generated code. Cover the smallest complete producer–boundary–consumer path for a cross-boundary defect.
4. Before reusing a graph, require a relevant decision question, source identity, language coverage, task scope and needed relation kinds. Refresh only invalidated anchors and necessary incoming/outgoing relations. Existing graph size is not evidence of relevance, and edits alone do not require an index rebuild.

Use available host tools and degrade to exact lookup when richer capabilities are absent. Do not silently install indexers, create databases, start services or scan the entire repository. Keep generated indexes and runtime evidence outside authoritative docs unless the repository explicitly owns those artifacts.

## Details only when needed

- For multihop ownership, dynamic flows, graph freshness or impact/test selection, read the relevant section of [navigation-and-evidence-rules.md](references/navigation-and-evidence-rules.md).
- For comparing or configuring a retrieval backend, read [tooling-options.md](references/tooling-options.md).
- During a real resume, consume identity and anchors already checked by the continuity owner. Do not repeat its audit or replace the saved mainline with a new exploration. New user questions and reminders do not invalidate otherwise current anchors.

Return the answer with stable file/symbol locators and the evidence limits that matter. Produce a graph, capability inventory or candidate-test list only when it helps the current decision; ordinary lookups need no fixed report template.
