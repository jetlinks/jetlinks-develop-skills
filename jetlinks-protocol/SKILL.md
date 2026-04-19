---
name: jetlinks-protocol
description: 在 JetLinks 协议包中处理协议支持注册、MQTT/HTTP/TCP/UDP/CoAP 编解码、Topic 或 path 路由、二进制报文读写、认证流程、协议文档与测试定位。适用于需要阅读或修改 ProtocolSupportProvider、DeviceMessageCodec、BinaryMessageType 等协议代码，排查上下行链路、认证失败、报文解析错误，或基于现有协议包样例实现新的传输接入方式。
---

# JetLinks Protocol

Read [`references/protocol-workflow.md`](references/protocol-workflow.md) first.

## Workflow

1. Classify the request as protocol reading, protocol implementation, binary packet analysis, or integration debugging.
2. Inspect protocol support registration first, then locate routes, config metadata, authenticators, and codec bindings.
3. Trace the upstream path from transport input to `DeviceMessage`, then trace the downstream path back to encoded packets, topics, or replies.
4. Read [`references/transport-codecs.md`](references/transport-codecs.md) when the task depends on MQTT, HTTP, TCP, UDP, CoAP, or WebSocket behavior.
5. Read [`references/binary-message-patterns.md`](references/binary-message-patterns.md) when the task involves framing, message types, ACK or reply correlation, sequence numbers, or dynamic data types.
6. Read [`references/example-locations.md`](references/example-locations.md) to find local docs, tests, and sample entry points before changing code.
7. Read [`references/debugging-checklist.md`](references/debugging-checklist.md) when the symptom is auth failure, message loss, bad routing, decode failure, or device/platform mismatch.
8. Reuse the existing protocol abstraction and update adjacent tests or protocol docs when the wire behavior changes.

## Required Constraints

- Do not assume fixed topics, HTTP paths, packet layouts, auth tokens, or message headers. Verify them from the current repository's provider, codec, docs, and tests.
- Do not fold product-specific device modeling rules into the generic protocol layer unless the repository already uses that boundary.
- Do not change binary field order, endian rules, or sequence correlation without checking compatibility and updating examples or tests.
- Do not implement only one direction of a protocol change. Verify both upstream decode and downstream encode when the transport supports both.
- If protocol changes cannot be verified in-session, state the exact pending test or debug commands and residual interoperability risks.
- Combine this skill with `$jetlinks-reactive` or `$jetlinks-delivery` when the task also changes reactive flows or requires commit or PR preparation.

## Response Shape

1. Task type and target transport or packet family
2. Confirmed protocol entry points
3. Upstream and downstream message path
4. Proposed code, test, and doc changes
5. Verification evidence and remaining protocol risks
