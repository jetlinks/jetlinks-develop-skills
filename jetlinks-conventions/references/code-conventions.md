# JetLinks 通用代码规范

按当前模块与依赖事实实现，不把相邻旧实现当成违反平台契约的依据。职责与通用性由 [职责规则](responsibility-and-generality-rules.md) 拥有，本文只补编码选择。

## 本地事实与命名

- 核验目标模块的包、基类、注解家族、执行模型及公开导出，不凭记忆生成 javax / jakarta、OpenAPI、事务或 CRUD 导入；不清时查 [导入参考](annotations-and-imports-reference.md)。
- 资源、权限、动作、命令、Topic 与 service / support ID 跟随实际契约，不自造平行命名。
- 保持范围内一致，不为小改动清理全部相邻代码；低上下文中的新约定应标为本次选择。

## 工具类

- 当前模块已有 Apache Commons 或相邻用法时，优先复用 ObjectUtils、ArrayUtils、CollectionUtils、MapUtils，不为几次判空新增依赖。
- 不禁用整个 StringUtils；按目标依赖实际 deprecated 状态选择 API。字符串比较、前后缀、包含、查找、普通替换 / 移除等操作，依赖提供 Strings 时使用 `Strings.CS / Strings.CI`。
- 不新增或扩散已废弃的 StringUtils 方法；依赖无 Strings 时选 JDK、Spring 或现有 helper，不为迁移写反射适配。正则操作使用 RegExUtils，null-safe 的 isEmpty / isBlank 等非废弃谓词可继续使用。
- 带默认值的字符串转换可使用 `Objects.toString(value, defaultValue)`，保留原有 null 与大小写语义。

## 可读性

- 链式调用表达同一层次的步骤，多阶段业务用命名方法和中间值；不为风格强制 Stream、fluent 或复杂设计模式。
- 纯转换可使用 map / filter；权限、持久化、远程调用、缓存写入和事件发布不能藏在 Java Stream 的 peek / map / filter 或外部可变状态中。
- 响应式链路的执行时机、操作符与资源边界由 [reactive](../../jetlinks-reactive/SKILL.md) 处理，不能把 Reactor map 与 Java Stream 的执行模型混为一谈。

## 专项规则归属

- 共享能力缺陷与 API 缺口：[根因处理](root-cause-and-no-hack-rules.md)。缺陷回到 owner 修复并提交 PR，不在调用方复制或特调规避。
- 公共类 / SPI、非显然业务、兼容、并发与生命周期：[注释规范](code-comments.md)。注释写在代码旁，不靠 PR 正文替代。
- 缓存、热路径、资源与历史：[运行状态](runtime-state-rules.md)。
- 国际化：[适用边界](i18n.md)，具体资源与 API 写法见 [用法](i18n-usage.md)。已有 i18n 模块的用户可见异常用 message key / i18nCode；无此机制时沿当前异常契约，不平行引入系统。
- 追踪与运维：[TraceHolder](tracing.md)、[MBean](mbean-observability.md)，复用已有覆盖，保护敏感数据。
- 发布与兼容：[后端设计规则](../../jetlinks-router/references/backend-design-test-driven-rules.md#发布边界与兼容性判断)。先核实发布、持久化与外部调用事实，再判断是否需要迁移；同 PR 中间实现不形成兼容负担。
