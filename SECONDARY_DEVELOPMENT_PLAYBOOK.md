# JetLinks 二开指南

面向需要跨阶段交付的开发任务。只按当前动作选技能，不把此指南变成所有任务的前置流程。

## 定位与边界

已知文件 / 符号用 [code-navigation](code-navigation/SKILL.md)，模块归属不明用 [routing](jetlinks-routing/SKILL.md)，技能入口不明才用 [router](jetlinks-router/SKILL.md)。

应用依赖平台和标准实体扩展遵守 [boundary](jetlinks-boundary/SKILL.md)：不依赖平台 manager 实现；跨服务业务调用走平台命令；声明式字段扩展核验 2.21 及目标制品能力，否则使用业务中间表。

## 实现

- 查询、写入、批量及状态动作使用 [CRUD](jetlinks-crud/SKILL.md)；数据权限由 [AssetsHolder](jetlinks-assets-permission/SKILL.md) 统一处理，普通业务字段不承载租户隔离模型。
- 事务共享连接串行、事务外有界并发及订阅执行使用 [reactive](jetlinks-reactive/SKILL.md)；触发时机与可靠交付使用 [events](jetlinks-events/SKILL.md)。不能将必须一致的本地清理全部移到提交后。
- 页面围绕真实任务与对象语义组织，读写一体、轻量原位编辑、复用真实组件；使用 [web](jetlinks-web/SKILL.md)，不默认传统全量表单。
- 职责、可读性、魔法值、通用策略、初始化与运行资源使用 [conventions](jetlinks-conventions/SKILL.md)。[通用组件缺陷](jetlinks-conventions/references/root-cause-and-no-hack-rules.md#通用组件缺陷的闭环) 在 owner 修复并提交 PR，不以调用方包装或特调替代。

按已明确目标直接推进，只有实质因果 / 契约未决才使用 [systematic-solving](systematic-solving/SKILL.md)。长任务状态与恢复由 [continuity](task-continuity/SKILL.md) 维护；有收益且获允许的委派由 [orchestration](agent-orchestration/SKILL.md) 管理。

## 验证与交付

后端行为变化使用 [设计与验证](jetlinks-router/references/backend-design-test-driven-rules.md)，围绕实际契约选择证据，阶段末集中验证；不为测试增加生产校验、不机械叠测试类型、不重跑仍有效证据。

审查请求用 [review](jetlinks-review/SKILL.md) 沿完整业务链取证；提交 / PR 按 [delivery](jetlinks-delivery/SKILL.md) 和已有授权完成。必要权威契约原位更新，运行态不写设计文档，测试证据留 PR / CI。

稳定知识确需沉淀时用 [capture](jetlinks-capture/SKILL.md)，不为完成任务自动创建总结或再次请求已取得的授权。
