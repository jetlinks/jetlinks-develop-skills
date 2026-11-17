---
name: code-navigation
description: 从文件或符号定位定义、调用关系、模块归属和变更影响，按证据逐步扩搜。普通定位不需要任务恢复或持久索引。
---

# Code Navigation

Own retrieval and evidence strength, not architecture choice or implementation. Start from the user's decision question and available anchor.

## Retrieval

1. Reuse current files, symbols and changed paths. Choose exact search for literals, semantic navigation for definitions / callers, build manifests for ownership, or bounded runtime evidence when static facts cannot decide.
2. Expand only through relations that can change the answer. Distinguish imports, build dependencies, resolved calls, possible dynamic targets and event / registration flows; similarity and inferred matches are candidates, not proof.
3. Check high-impact conclusions against current source, build facts or scoped observation. Preserve uncertainty for reflection, injection and generated code. Trace the smallest complete producer–boundary–consumer path needed for the question.
4. Reuse an index only when its source identity, language coverage, scope and relations fit this question. Refresh invalidated anchors and necessary relations, not the whole graph after every edit.

Use available tools and fall back to exact lookup. Do not silently install indexers, create databases, start services or scan the full repository. Keep generated evidence outside authoritative docs.

## Conditional details

- Multihop / dynamic flows, graph freshness or test impact: [navigation rules](references/navigation-and-evidence-rules.md).
- Comparing or configuring a backend: [tooling options](references/tooling-options.md).
- Actual resume: reuse identity and anchors already checked by the continuity owner; a new lookup is not a recovery event.

Return stable file / symbol locators and material evidence limits. Graphs, tool inventories and fixed reports are unnecessary for an ordinary lookup.
