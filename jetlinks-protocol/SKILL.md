---
name: jetlinks-protocol
description: 阅读、实现或排查 JetLinks 设备协议，包括注册、传输编解码、认证、二进制帧及请求应答关联。
---

# JetLinks Protocol

负责传输到 DeviceMessage 及其反向报文契约，不把产品专属业务建模混入通用协议层。

## 工作方式

1. 从 support / provider 注册定位传输绑定、路由、认证和 codec；路径不清时读 [协议链路](references/protocol-workflow.md)。
2. 依据真实文档、报文与相邻测试确认输入和预期输出，再跟踪上行与受影响的下行 / 应答路径。
3. 按任务读取：

| 任务 | 细则 |
| --- | --- |
| 新协议包或文档落地 | [开发模式](references/development-patterns.md) |
| MQTT / HTTP / TCP / UDP / CoAP / WebSocket | [传输规则](references/transport-codecs.md) |
| 帧、端序、类型、序号与 ACK | [二进制报文](references/binary-message-patterns.md) |
| 查找真实示例与报文 | [示例定位](references/example-locations.md) |
| 鉴权、丢消息、路由或解码故障 | [排查路径](references/debugging-checklist.md) |

## 关键约束

- topic、path、字段布局、认证和序号来自当前契约，不凭记忆编造报文。
- 先稳定传输与帧边界，再映射业务字段；变更兼顾受影响的编码、解码、应答与发布兼容性。
- ByteBuf 所有权、分片 / 粘包、重试 / 超时及断线资源按传输契约处理，不照搬复杂协议的缓存或状态机。
- 新增或改变协议行为时，按 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 使用代表报文验证受影响路径；不以无关构造包或 mock 绕过争议契约。
- 公共 codec / parser 契约与非显然 wire、认证、生命周期规则按 [注释规范](../jetlinks-conventions/references/code-comments.md) 写在代码旁。

交付实际支持的报文行为与验证结果；无法联调时明确剩余互通风险。
