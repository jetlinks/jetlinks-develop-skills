---
name: jetlinks-conventions
description: 应用 JetLinks 共享开发规则：职责与语义、通用策略、运行状态、编码与注释、i18n、追踪和运维观测。按当前问题读取对应细则。
---

# JetLinks Conventions

负责跨领域的代码与设计约定。模块落点归 routing，平台依赖与命令归 boundary，数据校验归 CRUD，授权归 AssetsHolder，响应式执行归 reactive；不要在此再定义一套领域规则。

## 使用方式

先核验相邻代码与当前依赖，只读取会改变本次决策的细则。已有事实和规则仍有效时复用，不因触碰文件扩展为无关清理。

公共设计或策略仅有样例 / 解法建议支撑时，按 [扩大依据的时机](../systematic-solving/references/systematic-solving-rules.md#扩大依据的时机) 定点核对规范与成熟实践；不等反复修补后才查证，也不为普通局部修改启动调研。

| 当前问题 | 规则 owner |
| --- | --- |
| 职责、抽象、语义命名、魔法值、配置、场景特调与初始化 | [职责与通用性](references/responsibility-and-generality-rules.md) |
| 缓存、派生状态、热路径、运行资源、历史 / 审计 | [运行状态](references/runtime-state-rules.md)；订阅取消等执行机制由 reactive 处理 |
| 工具类、导入家族、链式调用与 Java Stream 可读性 | [编码约定](references/code-conventions.md)；具体包 / 注解不清时查 [导入参考](references/annotations-and-imports-reference.md) |
| 公共类 / SPI 契约、非显然规则、兼容与并发注释 | [代码注释](references/code-comments.md) |
| 是否使用 i18n | [i18n 适用边界](references/i18n.md)；需要资源和 API 写法再读 [具体用法](references/i18n-usage.md) |
| 关键业务 span 与 Context 传播 | [追踪](references/tracing.md) |
| 常驻任务、缓存 / 队列、连接等运维观测 | [MBean](references/mbean-observability.md) |
| 工具 / SDK / 框架能力缺口 | [根因与扩展点](references/root-cause-and-no-hack-rules.md) |
| 后端行为契约与验证组织 | [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) |

## 关键约束

- 修共同根因和正确 owner，不为产品 ID、租户、路由或某次样例特调公共层；真实业务差异显式建模为策略或配置。纯复制转发、无用途留痕和无消费者抽象不增加价值。
- 公共标识、包路径和版本以代码 / 构建事实为准。长链按业务阶段拆分；纯转换保持普通函数，不在 Stream 的 `peek / map / filter` 中藏业务副作用。
- 先区分误用、能力缺口与通用组件缺陷；确认缺陷时在组件 owner 修复并提交 PR，不以业务包装、复制、深覆盖或特调规避。细则由 [根因处理](references/root-cause-and-no-hack-rules.md) 拥有。
- 同 PR 未发布中间形态直接收敛；只有已发布、持久化、外部依赖或用户明确要求的行为才设计兼容。
- 注释写公共契约及非显然原因，放在代码旁；明显实现不逐行复述，也无需逐文件报告“无需注释”。
- i18n、序列化、TraceHolder 与 MBean 复用当前平台能力。已有覆盖时不重复封装、埋点或加监控，不输出无关“不适用”清单。

阶段末验证受影响行为；向用户说明实际变化、关键理由、有效证据与剩余风险。维护约束时再查 [文献与适用边界](references/design-constraint-sources.md)，不加入普通任务必读链。
