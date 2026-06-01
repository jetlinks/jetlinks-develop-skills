# 文档落点规则

本文件用于判断 JetLinks 开发过程中哪些内容应该写入文档、写到哪里，以及什么时候不应该新增文档。

## 核心原则

0. Trellis 项目优先使用 Trellis artifact
   - 如果工作区存在 `.trellis/` 且有 active task，单次任务的 PRD、设计、任务拆分、测试目标和实现计划优先写入 `.trellis/tasks/<task>/prd.md`、`design.md`、`implement.md`。
   - 不为同一工作再创建 `docs/plans/...` 平行设计稿；长期架构规则稳定后再同步到既有 docs / ADR / `.trellis/spec/`。
   - 如果没有 active Trellis task，或用户明确要求不用 Trellis，继续按下方普通文档落点规则处理。

1. README 只放长期总览
   - 根 README：仓库定位、安装 / 使用入口、技能或模块索引、长期约定入口。
   - 模块 README：模块职责、核心能力、启动 / 配置入口、重要链接。
   - 不放单次任务过程、测试报告、PR 描述、临时计划、排查流水或大段设计取舍。

2. 先找已有归属文档
   - 先读根 README、AGENTS、docs 索引、模块 README、API 文档、已有 design / adr / plan。
   - 有明确归属时更新原文档，不新建平行文档。
   - 没有归属且内容不具备长期复用价值时，放在 PR 描述、issue、CI 结果或对话总结，不落长期文档。

3. 一个主题只保留一个主文档
   - 同一功能不要拆出多个 task、plan、test-report、summary 文档。
   - 设计、任务拆分、测试目标优先放在同一设计稿内。
   - 子任务细节放在设计稿的任务列表或 PR 描述中，除非它已经变成独立长期主题。

4. 测试证据不要污染说明文档
   - 测试命令、通过数、覆盖率、集成测试结果优先放 PR 描述或 CI 报告。
   - 设计稿只保留测试目标和必要的最终验证摘要。
   - README 不记录测试报告；除非 README 本身就是测试工具或质量门禁模块的长期使用说明。

5. 临时经验按项目工作流沉淀
   - Trellis 项目：稳定团队规则优先写 `.trellis/spec/`，单次任务过程和 journal 由 Trellis workspace / task 管理。
   - 非 Trellis 项目：单次任务复盘、排坑、工作记录默认走 `$jetlinks-capture`，项目内经验放 `.ai/worklog/`、`.ai/knowledge/`、`.ai/playbooks/`。
   - 多次验证后稳定、跨项目通用的内容，再升级为 prompt 或 skill。

## 落点决策表

| 内容 | 推荐落点 | 不推荐 |
| --- | --- | --- |
| 仓库 / 模块长期介绍 | 根 README 或模块 README | 每次任务都改 README |
| 较大功能设计、方案取舍、任务拆分、测试目标 | Trellis active task 下用 `.trellis/tasks/<task>/design.md` / `implement.md`；否则用既有 design / plans / adr 或最贴近模块的 docs 目录 | 只写在对话里，或同一任务同时写 Trellis artifact 和 docs plan |
| 架构决策、兼容性策略、长期边界规则 | `docs/adr/` 或既有架构文档 | 混在 PR 描述后丢失 |
| API、配置、启动方式、用户可见行为 | 既有 API / 模块说明 / 用户文档 | 放在测试报告或任务日志里 |
| 测试命令、覆盖率、CI 结果、集成测试结果 | PR 描述、CI 报告、测试报告目录（若项目已有） | README、模块说明、设计稿正文大段堆叠 |
| 单次排坑、复盘、经验 | Trellis 项目用 task / workspace journal；非 Trellis 项目用 `.ai/worklog/` 或 `.ai/knowledge/`，需用户确认 | 每个任务默认新增 docs 文档 |
| 稳定执行流程 | Trellis 项目用 `.trellis/spec/`；非 Trellis 项目用 `.ai/playbooks/`；成熟后升级 skill | 散落在多个任务总结 |

## 新增文档门槛

只有同时满足以下条件，才新增长期文档：

- 已确认没有合适的已有文档可更新。
- 内容未来会被人或智能体复用。
- 文档有清晰归属目录和维护对象。
- 文件名稳定可检索，避免 `temp`、`todo`、`note`、`summary` 这类泛名。

如果不满足，优先使用 PR 描述、issue、CI 结果或对话总结。
