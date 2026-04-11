# JetLinks AI 开发规则索引

本文件是 JetLinks 系脚手架的总路由，用来帮助智能体先判断任务类型，再切换到最合适的 focused skill，最后按当前工作区的真实实现落地。

它不提供仓库快照，不硬编码模块清单、包名、版本号或固定目录结构。所有这类信息都必须从当前工作区现有代码、`pom.xml`、资源目录和相邻模块中发现。

## 全局原则

1. 先发现，再实现
   - 不凭记忆假设模块名、注解包、依赖坐标、命令 ID、Topic、资源路径。
   - 先查看当前工作区的相邻代码、父子模块结构、现有配置和示例。

2. 只切换必要 skill
   - 本文件只做路由。
   - 进入某个场景后，只加载最少数量的 focused skill。

3. 优先复用现有抽象
   - JetLinks 系项目通常已经提供 CRUD 基类、命令服务、事件、订阅、国际化约定。
   - 默认沿用现有模式，不新增平行方案。

4. 以当前模块风格为准
   - 响应式或阻塞式、`javax` 或 `jakarta`、控制器基类、服务基类、i18n 路径，都以目标模块现状为准。
   - 仅在新建模块且没有可参考实现时，才基于通用规则做最小决策。

5. 生成最小可用实现
   - 只实现用户明确要求的内容。
   - 不额外生成示例实体、演示接口、假设性的扩展点。

6. 软链接模块同样属于工作区事实
   - 如果模块、组件或聚合目录是符号链接，不要忽略。
   - 需要同时识别“链接入口路径”和“真实目标路径”，必要时沿链接继续读取代码与配置。

7. 低上下文脚手架也要可工作
   - 如果当前仓库几乎没有业务代码、只有少量模板或只是空脚手架，不要停在“缺少参考实现”。
   - 在这种情况下，允许退化到“模板仓库模式”：基于根 `pom.xml`、目录结构、已有依赖和本规则集生成最小可用骨架。
   - 退化模式不仅适用于模块创建，也适用于 CRUD、权限、命令边界、事件驱动和基础 i18n 决策。

8. 一个任务可以同时使用多个 focused skill
   - 例如“新建模块并补 CRUD”通常会同时使用模块路由、通用规范和 CRUD skill。
   - 例如“改事件处理器并整理 PR”通常会同时使用事件订阅、响应式实践和 Git 交付 skill。

## 标准工作流

1. 分类任务
   - 判断这是结构发现、模块创建、CRUD、复杂查询、跨服务调用、实时订阅、事件驱动、国际化还是导入/注解确认。

2. 扫描当前工作区
   - 查看根目录、父 `pom.xml`、聚合模块、相邻模块、资源目录和已有实现。
   - 额外检查符号链接目录，确认是否有链接进来的外部模块、组件或子工程。

3. 切换最少 skill
   - 只切到覆盖当前任务的 focused skill。

4. 找相邻示例
   - 在目标模块或相似模块中定位同类实现。
   - 如果示例位于软链接模块中，允许沿链接读取其真实内容。
   - 如果没有相邻示例，切换到模板仓库模式，按通用规则生成最小实现。

5. 实现
   - 复用现有抽象，保持命名、分层、注解和返回类型一致。

6. 校验
   - 检查依赖、注解、导入、编程模型、权限、i18n、事件或 Topic 是否与当前工作区一致。

7. 交付
   - 如果任务包含提交、推送或发 PR，切换到 `$jetlinks-delivery`。
   - 先跑改单涉及的单元测试或集成测试，再整理 commit 和 PR 信息。
   - 输出测试命令、通过数、失败数、跳过数和覆盖率数据。

## 任务路由

### 先看哪些模块、能力和目录

切换：
- [`$jetlinks-routing`](../../jetlinks-routing/SKILL.md)

适用：
- 不知道代码应该落在哪个模块
- 不知道当前脚手架有哪些业务域、组件域、聚合模块
- 不确定新功能应该挂到现有模块还是新建模块

### 判断“直接依赖 / 命令调用 / 事件 / 订阅”

切换：
- [`$jetlinks-boundary`](../../jetlinks-boundary/SKILL.md)

适用：
- 需要使用其他模块能力
- 不确定是加 Maven 依赖、调用命令服务、发布事件还是订阅消息
- 空脚手架中首次建立模块边界约定

### 协议包 / 编解码 / 二进制报文

切换：
- [`$jetlinks-protocol`](../../jetlinks-protocol/SKILL.md)

适用：
- 需要修改 `ProtocolSupportProvider`、`DeviceMessageCodec`、传输路由或认证流程
- 需要分析 MQTT、HTTP、TCP、UDP、CoAP 等协议接入方式
- 需要阅读或调整二进制报文、ACK、消息序号或属性和功能消息映射

### 确认注解、包名、导入

切换：
- [`$jetlinks-conventions`](../../jetlinks-conventions/SKILL.md)

适用：
- 不确定 `javax`/`jakarta`
- 不确定实体、控制器、事件、命令、订阅的注解和导入

### 创建新模块或聚合模块

切换：
- [`$jetlinks-routing`](../../jetlinks-routing/SKILL.md)

适用：
- 新建 manager/core/adapter 模块
- 调整聚合 `pom.xml`、自动配置、资源目录
- 空脚手架中首次创建业务模块

### 标准 CRUD

切换：
- [`$jetlinks-crud`](../../jetlinks-crud/SKILL.md)

适用：
- Entity / Service / Controller 的常规新增或修改
- 标准增删改查
- 权限、校验、基础 i18n
- 空脚手架中首次创建基础 CRUD 骨架

### 复杂 CRUD / 查询 / 批处理

切换：
- [`$jetlinks-crud`](../../jetlinks-crud/SKILL.md)

适用：
- 复杂条件查询、分页、聚合、批量修改、关系同步
- CRUD 伴随复杂副作用

### 跨服务或跨边界调用

切换：
- [`$jetlinks-boundary`](../../jetlinks-boundary/SKILL.md)

适用：
- 命令服务
- 服务代理
- 远程查询和远程操作

### 实时消息 / Topic 订阅

切换：
- [`$jetlinks-events`](../../jetlinks-events/SKILL.md)

适用：
- `@Subscribe`
- EventBus/Topic 流式处理
- 设备消息、系统消息、广播消息

### 领域事件 / 生命周期事件

切换：
- [`$jetlinks-events`](../../jetlinks-events/SKILL.md)

适用：
- `@EventListener`
- 实体新增、修改、删除后的副作用
- 事务提交后的异步处理

### 国际化

切换：
- [`$jetlinks-conventions`](../../jetlinks-conventions/SKILL.md)

适用：
- 新增枚举、实体字段、权限、操作、错误消息、提示消息

### 提交、分支、PR 与测试交付

切换：
- [`$jetlinks-delivery`](../../jetlinks-delivery/SKILL.md)

适用：
- 需要 commit、push、发起 PR
- 需要起草或审查中文 commit message
- 需要生成 shell 可执行的 git commit 命令
- 需要整理提交信息、PR 标题或 PR 描述
- 需要确认是否允许直接推送到目标分支
- 需要给出测试和覆盖率证明

## 常见组合

- 新建模块并提供 CRUD
  - `$jetlinks-routing`
  - `$jetlinks-crud`
  - `$jetlinks-conventions`

- 在现有模块补一个查询接口
  - `$jetlinks-routing`
  - `$jetlinks-crud`
  - 如模块是响应式，再加 `$jetlinks-reactive`

- 调用其他模块能力
  - `$jetlinks-boundary`
  - 如是响应式模块，再加 `$jetlinks-reactive`

- 修改协议包或联调设备接入
  - `$jetlinks-protocol`
  - 如涉及提交与测试证据，再加 `$jetlinks-delivery`

- CRUD 后要同步其他数据
  - `$jetlinks-crud`
  - `$jetlinks-events`
  - 如涉及响应式链路，再加 `$jetlinks-reactive`

- 处理设备或系统消息流
  - `$jetlinks-events`
  - 如需要持久化或反查实体，再加 `$jetlinks-crud`

- 提交并发起 PR
  - `$jetlinks-delivery`
  - 如改动涉及具体模块，再加对应业务 skill

## 输出要求

### 当用户要求先分析

输出：
1. 任务分类
2. 需要切换的 focused skill
3. 需要先确认的工作区事实
4. 建议落点和实现边界
5. 如果当前仓库参考实现很少，明确说明将切换到模板仓库模式

### 当用户要求直接实现

执行顺序：
1. 静默完成分类
2. 切换最少 focused skill
3. 查看相邻代码
4. 直接实现
5. 如果任务要求交付，再补测试、提交与 PR 规范检查
6. 总结本次遵循的规则和验证结果
