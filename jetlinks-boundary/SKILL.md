---
name: jetlinks-boundary
description: 选择并复用 JetLinks 平台能力，处理告警、计算、通知等业务接入、依赖边界、字段 / 对象建模与跨服务命令。模块落点由 jetlinks-routing 处理。
---

# JetLinks Boundary

负责平台能力选型、依赖方向、公开契约和跨边界交互方式；权限判定归 AssetsHolder，消息交付归 events。

## 工作方式

1. 业务要增加告警、公式 / 指标计算、通知等同类功能时，先按 [平台能力复用](references/platform-capability-reuse-rules.md) 判断配置、组合、SPI 扩展或独立业务语义，不先创建平行实现。确认 owner、目标版本、部署边界和公开契约；构建依赖、提供方和消费者是事实源。
2. 应用依赖平台或扩展标准实体时，读 [应用与平台规则](references/application-platform-rules.md)；负责人、归属等对象建模读 [属性与对象关系选择](references/object-modeling-rules.md)；交互方式尚不明确时查 [边界选择](references/module-reference.md)。
3. 实现命令提供方、消费者或代理时，读 [命令调用](references/cross-service-call-rules.md)。核实 service / support / command ID、载荷、Context、结果与失败语义，不凭方法名猜契约。
4. 新增或改变后端契约时，按 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 选择受影响的行为证据。

## 不可遗漏

- 应用禁止直接依赖 `device-manager`、`authentication-manager` 等平台标准实现模块；同进程、optional / provided scope 或转导出实现类型均不构成例外。
- 跨服务业务调用使用平台命令，不能以实现类注入、直连对方数据库或旁路 HTTP 绕开契约。同一业务边界内的本地公开 API / SPI 不必伪装为远程调用。
- 对象、关系和语义由业务通过 relation / core 契约及注解声明，业务不依赖任何 ontology 模块；本体在上层消费。先区分属性、关系和独立业务对象，再按版本及事实 owner 选择实现，不能都归为新增字段。
- 已有显式命令类时，复用命令对象与 `commandSupport.execute(...)`；保持响应式边界非阻塞。
- 传递可信身份 / 权限 / trace Context；超时不等于未执行，本地事务不能回滚远端副作用。权限实现按 [AssetsHolder](../jetlinks-assets-permission/SKILL.md)。

只解释实际选择及契约风险；验证真实载荷、权限传播、结果与必要的失败恢复，不 mock 掉本次正在选择的边界。
