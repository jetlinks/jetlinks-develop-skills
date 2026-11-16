---
name: jetlinks-assets-permission
description: 通过 JetLinks AssetsHolder 实现数据权限，核对资产实体声明、动作、关联映射及查询、命令、订阅等独立入口的授权 owner。
---

# JetLinks Assets Permission

负责数据授权契约；业务关系字段、功能权限和资产数据权限各有用途，不能相互替代。

## 工作方式

1. 从实体的 @Asset、ExtendableEntity 继承关系开始，核验 AssetType、CrudAssetPermission、绑定关系、控制器基类及命令 / 订阅的权限入口。
2. 按 [AssetsHolder 规则](references/assets-holder-rules.md) 选择自有资产、关联资产、查询注入、动作校验或消息过滤。记录本次改变的主体、资产、动作与唯一 owner 即可，不展开全层矩阵。
3. 先查目标版本契约和现有用法；只有仍未确定、会改变访问范围的业务归属或例外语义才询问用户，不能自行全放行或全拒绝。

## 关键约束

- 受资产数据权限控制的实体必须声明 `@Asset` 并继承平台 `ExtendableEntity<K>`；已有基类已满足继承时直接复用。资产类型、ID 字段及关联映射按 [实体契约](references/assets-holder-rules.md#资产实体契约) 核验，DTO 不因传递资产 ID 而套用实体继承。
- 使用平台 holder / dimension / asset 契约，禁止手写租户、机构、部门或创建人过滤替代统一权限。
- 普通业务 Entity / DTO / 命令不以新增 `tenantId` 等部署隔离字段另建权限模型。真实领域关系及权限 Provider 内部实现需按其职责区分。
- 优先 `AssetsHolderCrudController` / `CorrelatesAssetsHolderCrudController` 等现成 owner；已检查同一动作时，调用方和 Service 不复制检查。独立暴露且主体、资产或动作不同的入口仍须授权。
- `@AssetsController(ignore = true)` 的受保护端点必须有等价的查询注入、动作校验或资产过滤。
- 查询、分页、统计、批量、导出、命令和订阅不能绕开权限；空 holder 的行为按平台契约判断，不从一个空值推导全部授权。
- 本次边界变化验证最小真实 allow / deny，关联、批量和不同动作仅按变化补充；不重测未改框架全套行为，不将 holder mock 为永远通过。

说明实际权限 owner、集成方式和未解决语义；非显然映射与例外在代码旁说明。
