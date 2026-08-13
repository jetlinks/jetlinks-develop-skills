# JetLinks 系统性求解扩展

本文件只补充 JetLinks 工作区的领域与实施映射。通用问题模型和停滞门禁以 [`../../systematic-solving/SKILL.md`](../../systematic-solving/SKILL.md) 为准；计划压缩、恢复协议、证据复用和阶段性交付以 [`../../task-continuity/SKILL.md`](../../task-continuity/SKILL.md) 为准，不在这里复制。

## 1. 任务状态映射

- 先由 `$task-continuity` 建立环境无关状态协议；检测到 `.trellis/` 时，再按 [`trellis-integration-rules.md`](trellis-integration-rules.md) 发现本地 workflow、task、research、runtime 和跟踪策略，不能把某个项目的 Trellis 布局当成全局约定。
- 没有 Trellis 时，按 [`document-placement-rules.md`](document-placement-rules.md) 复用已有 task / agent runtime；确实没有时才使用经 Git 忽略验证的单一 sidecar。
- JetLinks Recovery Capsule 与 Source Snapshot 使用 [`context-recovery-rules.md`](context-recovery-rules.md) 将通用语义状态和源码身份分别映射为 route / evidence / Next 与 branch / HEAD / tracked / untracked / nested digest / expected paths；Git 是本仓库交付适配，不是通用技能依赖。
- 实时计划、假设、失败和胶囊不进入权威 docs；任务契约和稳定设计是否受跟踪按本地 workflow 与文档归属决定。

## 2. 领域系统图

当 JetLinks 复杂链路涉及下列关系时，组合 `$code-navigation` 与 [`code-navigation-jetlinks-rules.md`](code-navigation-jetlinks-rules.md)：

- Module / Command / CommandHandler / Provider / Proxy 的所有权与边界。
- DomainEvent / LifecycleEvent / Topic / Subscription 的生产、传递和消费。
- AssetsHolder / AssetType / permission action / QueryParam 的权限注入与过滤。
- Protocol / transport / codec / parser / device message / reply correlation 的上下行链路。
- Controller / DTO / Entity / storage / cache / scheduler 的状态与生命周期。
- Vue route / component / store / API client / EnumDict 的前后端承载关系。
- TraceHolder / MonoTracer / FluxTracer 与 MBean 的观测边界。

这些节点和边是领域候选，必须由当前工作区真实存在的语言、构建声明、注册配置、源码或运行时证据确认。不得因 JetLinks 常用 Java、Maven 或 Vue 就假设目标仓库一定提供它们。

## 3. 实施与验证映射

- 由相应 JetLinks focused skill 负责 CRUD、响应式、边界、事件、协议、权限、前端和编码规范；`$systematic-solving` 只负责问题模型、停滞止损、解法层级和验证矩阵。
- 共享能力变化至少验证原场景、一个同类代表、一个反例 / 边界和主要回归；局部缺陷不为凑矩阵而扩成公共框架。
- 同一验证批次中的失败先分为生产契约缺陷、陈旧 consumer / oracle、无效 fixture、机械装配或 unresolved；只有违反同一 JetLinks 不变量的生产失败进入同一实现切片。
- 在连贯阶段完成并集中验证后，交给 `$jetlinks-delivery` 创建一个本地 commit，并把实际 commit 与 Git 指纹写入非版本化 Recovery Capsule。
- 所有阶段与总体验收完成前不 push、不创建或更新 PR；用户明确要求共享中间状态时只更新同一个 draft，不创建步骤 PR。
- 交付前先映射已有测试证据；tree / diff、相关测试、配置、依赖、base、环境和检查语义未失效的证据直接复用，只补跑缺失、失效或有时效性的范围。
