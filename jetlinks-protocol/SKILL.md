---
name: jetlinks-protocol
description: 在 JetLinks 协议包中阅读、实现或排查协议注册、传输编解码、二进制报文、Topic / path 路由、鉴权、物模型映射和应答关联。适用于协议文档落地、样例报文分析或设备接入调试。
---

# JetLinks Protocol

Use [`references/protocol-workflow.md`](references/protocol-workflow.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

## Workflow

1. Classify the request as protocol reading, protocol implementation, binary packet analysis, or integration debugging.
2. If this creates a new protocol package or changes protocol behavior, first follow [`../jetlinks-router/references/backend-design-test-driven-rules.md`](../jetlinks-router/references/backend-design-test-driven-rules.md): reuse or record the task contract, relevant protocol examples and test goals; apply its authorization rule and synchronize accepted durable wire contracts when needed.
3. Inspect protocol support registration first, then locate routes, config metadata, authenticators, and codec bindings.
4. Trace the upstream path from transport input to `DeviceMessage`, then trace the downstream path back to encoded packets, topics, or replies.
5. Read [`references/development-patterns.md`](references/development-patterns.md) when creating a new protocol package or turning a protocol document into implementation tasks.
6. Read [`references/transport-codecs.md`](references/transport-codecs.md) when the task depends on MQTT, HTTP, TCP, UDP, CoAP, or WebSocket behavior.
7. Read [`references/binary-message-patterns.md`](references/binary-message-patterns.md) when the task involves framing, message types, ACK or reply correlation, sequence numbers, or dynamic data types.
8. Read [`references/example-locations.md`](references/example-locations.md) to find local docs, tests, and sample entry points before changing code.
9. Read [`references/debugging-checklist.md`](references/debugging-checklist.md) when the symptom is auth failure, message loss, bad routing, decode failure, or device/platform mismatch.
10. Before implementing or changing protocol code, identify comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md): Provider / Codec / parser public contracts, wire compatibility, endian / framing assumptions, ACK or sequence correlation, ByteBuf lifecycle, auth boundary, retry / timeout, and transport-specific deviations.
11. Reuse the existing protocol abstraction and update adjacent tests or protocol docs when the wire behavior changes.
12. Use [systematic-solving Admission](../systematic-solving/SKILL.md#admission) to decide whether this problem needs structured investigation. It owns hypotheses, evidence and stagnation control; this skill owns the domain implementation. A known cross-layer change or approved retry / mock is not itself an admission signal.

## Required Constraints

- Do not assume fixed topics, HTTP paths, packet layouts, auth tokens, or message headers. Verify them from the current repository's provider, codec, docs, and tests.
- Do not fold product-specific device modeling rules into the generic protocol layer unless the repository already uses that boundary.
- Do not change binary field order, endian rules, or sequence correlation without checking compatibility and updating examples or tests.
- Do not implement only one direction of a protocol change. Verify both upstream decode and downstream encode when the transport supports both.
- Do not start from business-field mapping before the transport boundary and frame boundary are stable.
- Do not make simple protocols carry complex caches, state machines, or split packages just because another protocol does; add those only when the protocol explicitly needs them.
- Do not implement a new protocol or large wire-behavior change until the relevant contract and validation goals are clear under the authorization rule in [backend design](../jetlinks-router/references/backend-design-test-driven-rules.md).
- Do not make protocol tests pass with invented packets that ignore the real document or adjacent examples; validate representative registration, auth, framing, decode, encode, ACK, error, and compatibility cases.
- Do not leave protocol providers, codecs, parsers, packet registries, or compatibility branches comment-free when they encode wire contracts, framing / endian assumptions, ACK or sequence correlation, ByteBuf lifecycle, auth boundary, or transport-specific deviations. Add concise code comments and complete public contract comments where implementers depend on them.
- If protocol changes cannot be verified in-session, state the exact pending test or debug commands and residual interoperability risks.
- Combine this skill with `$jetlinks-reactive` or `$jetlinks-delivery` when the task also changes reactive flows or requires commit or PR preparation.

## Response Shape

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

1. Task type and target transport or packet family
2. Confirmed protocol entry points
3. Upstream and downstream message path
4. Task-contract path, authoritative-doc sync decision, and test goals when the backend design gate applies
5. Proposed code, test, and doc changes
6. Comment targets added, or the concrete reason no code comments were needed
7. Verification evidence and remaining protocol risks
