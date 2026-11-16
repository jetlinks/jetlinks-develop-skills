---
name: jetlinks-review
description: 沿真实业务链路审查 JetLinks 代码、PR、方案或任务累计改动的正确性、安全、生命周期和维护成本。开发规则由对应领域技能拥有。
---

# JetLinks Review

负责审查路径、证据和判定；开发时直接执行领域规则，不等待审查触发。本技能不自动授权修复、提交或发布。

## 审查路径

1. 确认对象、基线、目标版本与范围；区分 PR diff、工作树和方案。整体审查沿相关入口与契约扩展，不默认扫描整个仓库。
2. 沿 **入口 → 业务决策 / 状态 → 持久化 / 外部能力 → 返回 / 后续消费者** 追完整路径。任务、命令、订阅和回调同样是入口。
3. 按变化选择下面的切片与规则；不在表中的场景也用同一路径。先看结果、安全和恢复，再判断职责、复杂度与通用性。
4. 按 [证据与判定](references/review-method.md) 核对触发、影响、位置和合理反例；关键词命中、历史意见或个人偏好不是当前缺陷证据。

共享契约、跨边界行为、公共能力替换或跨仓接入发生实质变化，或用户要求全局审查时，按 [任务整体审查](references/review-method.md#任务整体审查) 覆盖累计改动与消费者；不以文件数、行数或技术关键词触发全套流程。

## 按需切片

| 场景 | 开发规则 owner |
| --- | --- |
| 建模、职责、依赖与字段扩展 | [职责语义](../jetlinks-conventions/references/responsibility-and-generality-rules.md)、[平台边界](../jetlinks-boundary/references/application-platform-rules.md)；受控实体查 [资产实体契约](../jetlinks-assets-permission/references/assets-holder-rules.md#资产实体契约) |
| 查询、树、关联、统计与历史 | [查询与规模](../jetlinks-crud/references/advanced-crud-rules.md)、[权限](../jetlinks-assets-permission/SKILL.md) |
| 写入、删除、导入导出、批量与部分失败 | [CRUD](../jetlinks-crud/SKILL.md) |
| 审批、支付、认领、发布等状态动作 | [状态与重复请求](../jetlinks-crud/references/common-crud-rules.md#状态流转与重复请求) |
| 命令、第三方适配、回调或工具调用 | [调用与恢复](../jetlinks-boundary/references/cross-service-call-rules.md) |
| 事件、通知、持续订阅与历史实时交接 | [events](../jetlinks-events/SKILL.md) |
| 规则、流程、调度、缓存、队列与资源 | [运行状态](../jetlinks-conventions/references/runtime-state-rules.md)、[事务与并发](../jetlinks-reactive/SKILL.md) |
| DTO、序列化、配置、插件与协议 | [数据契约](../jetlinks-conventions/references/responsibility-and-generality-rules.md#数据契约与配置)、[protocol](../jetlinks-protocol/SKILL.md) |
| 前端列表、详情、配置与异步状态 | [web](../jetlinks-web/SKILL.md) |
| 安装、迁移、初始化、兼容、审计与交付 | [通用性](../jetlinks-conventions/references/responsibility-and-generality-rules.md)、[运行留痕](../jetlinks-conventions/references/runtime-state-rules.md#历史审计与可观测性)、[delivery](../jetlinks-delivery/SKILL.md) |

需要沿代码展开或检查反例时查 [场景链路](references/scenario-review-map.md)。[历史与文献依据](references/design-sources.md) 和 [正反评估场景](references/evaluation-cases.md) 用于维护或特定疑点，不是普通审查必读链。

## 输出

报告可行动发现：准确位置、触发条件、实际后果及 owner 层修复方向，同一根因合并。行为 / 安全缺陷与维护改进区分，后者说明具体成本。无实质问题时直接说明范围与未验证边界，不凑数量。

验证在连贯阶段末按风险集中完成；静态规则检查和旧分支测试不能证明当前业务正确。
