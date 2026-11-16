---
name: jetlinks-boundary
description: 选择并实现 JetLinks 应用与平台的依赖边界、标准实体字段扩展和跨服务命令。模块落点由 jetlinks-routing 处理。
---

# JetLinks Boundary

负责依赖方向、公开契约和跨边界交互方式；权限判定归 AssetsHolder，消息交付归 events。

## 工作方式

1. 确认能力 owner、目标版本、部署边界和已公开的 core / API / command / SPI；构建依赖、提供方和消费者是事实源。
2. 应用依赖平台或扩展标准实体时，读 [应用与平台规则](references/application-platform-rules.md)；交互方式尚不明确时查 [边界选择](references/module-reference.md)。
3. 实现命令提供方、消费者或代理时，读 [命令调用](references/cross-service-call-rules.md)。核实 service / support / command ID、载荷、Context、结果与失败语义，不凭方法名猜契约。
4. 新增或改变后端契约时，按 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 选择受影响的行为证据。

## 不可遗漏

- 应用禁止直接依赖 `device-manager`、`authentication-manager` 等平台标准实现模块；同进程、optional / provided scope 或转导出实现类型均不构成例外。
- 跨服务业务调用使用平台命令，不能以实现类注入、直连对方数据库或旁路 HTTP 绕开契约。同一业务边界内的本地公开 API / SPI 不必伪装为远程调用。
- 标准实体扩展：2.21 及以后核验目标制品的注解能力与主实体启用；更早或制品无能力时用业务中间表。不能仅凭源码注释判断已发布支持。
- 已有显式命令类时，复用命令对象与 `commandSupport.execute(...)`；保持响应式边界非阻塞。
- 传递可信身份 / 权限 / trace Context；超时不等于未执行，本地事务不能回滚远端副作用。权限实现按 [AssetsHolder](../jetlinks-assets-permission/SKILL.md)。

只解释实际选择及契约风险；验证真实载荷、权限传播、结果与必要的失败恢复，不 mock 掉本次正在选择的边界。
