---
name: jetlinks-routing
description: 发现 JetLinks 工作区、确认模块归属并按需创建模块。已知文件或符号的定位使用 code-navigation；模块间交互使用 jetlinks-boundary。
---

# JetLinks Routing

负责代码放在哪里，不决定跨模块如何调用。已有可信模块锚点时，只核对相关构建声明，不重新盘点工作区。

## 工作方式

1. 从根目录、聚合构建声明和软链接确认候选模块，按 [模块发现](references/module-list.md) 补必要事实。目录邻近、import 或图聚类不能证明 Maven 归属。
2. 优先扩展现有业务模块；只有职责确无归属时，按 [模块创建](references/module-creation-rules.md) 建最小结构，不因样例缺失另起模块。
3. 新增后端模块或能力时，使用 [设计与验证](../jetlinks-router/references/backend-design-test-driven-rules.md) 明确改变的契约和验收，复用已有授权。

## 关键边界

- 遵循当前构建与注册方式，不硬编码全量模块清单、不遗漏软链接、不顺手重排无关模块。
- 采用 `manager / core` 分层的工作区：CRUD、控制器、持久化、权限及运行装配归 manager；共享 DTO、命令、事件、SPI 等契约归 core，不默认创建 `xxx-api`。
- 应用依赖平台实现或扩展标准字段时，转到 [平台边界](../jetlinks-boundary/references/application-platform-rules.md)，不能从“放在一起”推导可直接依赖。
- 新公共契约和装配入口按 [注释规则](../jetlinks-conventions/references/code-comments.md) 说明职责与扩展边界。

说明选定落点及必要理由；创建或调整结构后集中验证相关构建、注册和加载路径。
