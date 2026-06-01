# Trellis 集成调度规则

本文件用于 JetLinks skills 运行在 Trellis 项目中时的职责边界。检测到工作区存在 `.trellis/` 时优先遵守本文件。

## 总原则

- Trellis 是工作流主控：负责任务创建、PRD、design、implement plan、状态流转、continue、finish、archive 和 journal。
- JetLinks skills 是领域能力模块：负责模块落点、CRUD、资产权限、边界调用、事件、响应式、协议、前端交互、编码规范和交付门禁。
- focused skill 不主动创建 Trellis task、不归档 task、不写 journal、不切换 active task，除非用户明确要求操作 Trellis。
- JetLinks router 只输出 JetLinks 领域路由和门禁结论；完成后把控制权交还 Trellis 当前阶段。

## 文档落点

- 如果存在 active Trellis task，大后端设计、测试目标、任务拆分优先写入 `.trellis/tasks/<task>/design.md` 和 `.trellis/tasks/<task>/implement.md`。
- `prd.md` 承载需求、范围、验收标准；`design.md` 承载 JetLinks 特有设计门禁；`implement.md` 承载步骤、验证命令和回滚点。
- 不同时创建 `docs/plans/...` 和 `.trellis/tasks/...` 两套设计稿。
- 如果没有 active Trellis task，仍按 `document-placement-rules.md` 选择现有 docs / plans / adr 位置。

## 知识沉淀

- Trellis 项目内的稳定团队规则优先写入 `.trellis/spec/`。
- 单次任务过程、复盘和 journal 归 Trellis workspace / task 管理，不默认写 `.ai/`。
- 只有结论稳定、跨任务、适合所有 JetLinks 项目复用时，才建议更新 `jetlinks-develop-skills` 并准备官方 skill PR。

## 交付边界

- `jetlinks-delivery` 负责 commit 标题、分支策略、测试证据、PR 描述和 JetLinks 后端门禁。
- Trellis `finish-work` 负责 task archive 和 session journal；JetLinks skills 不替它归档。
- 在 Trellis 项目中，work commit 可以按 JetLinks delivery 规范生成；archive / journal commit 顺序由 Trellis finish 流程维护。
- 如果 Trellis finish 要求 clean tree，先清理或隔离与本次任务无关的未跟踪文件。只有当产物规则具备项目级长期价值且用户确认时，才把 `.gitignore` 变更纳入工作提交。

## 调度输出

Trellis 场景下，router 分析应附加：

1. Trellis phase：planning / in_progress / finish / no active task / unknown
2. JetLinks focused skills：本次需要的 focused skill 列表
3. Artifact target：`.trellis/tasks/<task>/...` 或非 Trellis 文档位置
4. Lifecycle owner：Trellis
5. Handoff：回到 Trellis continue / implement / check / finish-work，或继续当前 inline turn

## 反模式

- skill 自行创建 `.trellis/tasks` 之外的平行计划文档。
- focused skill 在实现中途归档任务或写 journal。
- delivery 在 Trellis archive 之前把 task archive / journal 当作普通工作提交处理。
- capture 同时写 `.ai/knowledge` 和 `.trellis/spec` 表达同一条稳定规则。
