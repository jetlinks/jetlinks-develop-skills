---
name: jetlinks-crud
description: 实现 JetLinks 实体、查询、写入、状态动作及导入导出。复用当前 CRUD 抽象，按需处理校验、批量与数据权限。
---

# JetLinks CRUD

负责数据操作与状态不变量；权限规则归 AssetsHolder，事务执行归 reactive，外部联动归 events / boundary。

## 工作方式

1. 核验目标模块的响应式 / 阻塞模型、Entity / Service / Controller 基类及相邻实现，按 [基础 CRUD](references/common-crud-rules.md) 选择最小完整变化。
2. 新增或改变后端行为时，按 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 明确受影响契约与证据；不为已明确需求另建审批。
3. 按当前操作读取细则，不整套加载：

| 操作 | 细则 |
| --- | --- |
| QueryParam、条件 DSL、排序、分页、QueryHelper 或 SQL | [查询 DSL](references/query-dsl-rules.md) |
| 关联、汇总、批量、副作用、导入导出与部分失败 | [高级 CRUD](references/advanced-crud-rules.md) |
| 自定义 termType、条件映射、关联表 exists | [动态条件](references/dynamic-term-rules.md) |
| 审批、认领、发布 / 撤销等可重放动作 | [状态与重复请求](references/common-crud-rules.md#状态流转与重复请求) |
| 标准实体新增业务字段 | [版本化字段扩展](../jetlinks-boundary/references/application-platform-rules.md#标准实体字段扩展) |
| 负责人、归属、对象关联或任职事实的建模 | [属性与本体关系选择](../jetlinks-boundary/references/object-modeling-rules.md) |
| 新增或改变数据权限边界 | [AssetsHolder](../jetlinks-assets-permission/SKILL.md) |

## 关键约束

- 先复用基类、CRUD DSL、QueryParam、QueryHelper 和既有批量能力，不重复造端点、筛选 DTO、逐行写入或手工分页装配；真实置空使用 `setNull(...)`。
- 输入格式与范围归 DTO / 框架，权限归权威入口，状态 / 持久化不变量归服务事务，危险空条件操作归操作 owner。保留独立安全边界，不在同链各层重复校验，也不为异常测试新增生产 guard。
- 权限条件应在分页、count、汇总之前生效；查询、详情、动作、批量和导出都要识别其 owner，不能只保护普通列表。
- 批量先确定整批原子、分批提交或逐项结果；失败后逐条重放必须有原子性或幂等保障。
- 必须一致的本地联动留在事务内；外部交付按 [事件规则](../jetlinks-events/SKILL.md) 选择时机与恢复方式。
- 事务共享连接串行操作，事务外并发按 [reactive](../jetlinks-reactive/SKILL.md) 限制；不要用并发掩盖 N+1。
- 优先可移植 SQL；查询形态、规模、索引、分页或批量风险变化时才补相称性能证据。
- 复杂 DSL 按业务阶段命名；注释、工具类和 i18n 沿用 [编码规范](../jetlinks-conventions/SKILL.md)，不另起风格。

阶段结束集中验证实际改变的数据结果、权限和状态语义；交代真实未覆盖风险。
