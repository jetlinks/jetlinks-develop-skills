# JetLinks Web Example Locations

交互参考统一从 `jetlinks-web-core` 的自包含场景进入。当前用户指定的原型和已接受路径仍是本次改造依据；示例只补充实现模式，不覆盖业务契约。

## 场景入口

定位目标前端工作区的 `jetlinks-web-core/src/views/interaction-examples/README.md`，只打开当前场景：

| 场景 | Core 内文件 | 核对重点 |
| --- | --- | --- |
| 四类企业场景入口 | `SemanticWorkspace.vue`、`semantic-scenarios.md` | 可运行台账、业务联动、规则 / 流程、项目设置；按当前 runtime-ui 真实组件组合，设计说明标明各场景能力范围 |
| 左分区与右列表 | `SceneRecordList.vue`、`useSemanticExamples.ts` | `EqualHeightColumns`、`QuickFilterSidebar`、`ConditionFilter`、`j-pro-table` 与 `j-badge-status`；共用筛选条件，保留分页，详情返回恢复定位，窄屏分区抽屉 |
| 关联处置与对象详情 | `AssetSceneDetail.vue`、`IncidentSceneDetail.vue` | 顶部工具栏承载身份，真实 `ResponsiveGrid`、`Editable`、List / Statistic 与时间线；资料、事实、关系依业务顺序阅读，处置动作与过程相邻，跨对象返回 |
| 规则、流程与设置 | `RuleSceneDetail.vue`、`SettingsScene.vue` | 草稿与生效版本、样本过期、流程定义与执行实例；设置分组草稿与整组应用，图文渠道选项改变内容，新建采样默认值接续 |
| 创建与接续 | `FormExample.vue`、`usePointWorkspace.ts` | 直接输入名称、图标多选决定实际采集内容、常用间隔与自定义；整组校验，创建后进入同一对象 |
| 对象详情 | `PointWorkspace.vue`、`DetailExample.vue`、`ContentNote.vue` | 采集设置与信号规则同页，字段与语句参数原位编辑；同处核对已应用读数，保留只读与局部错误 |
| 连续配置与规则 | `ConfigurationExample.vue` | 换算、条件、样本验证、应用的顺序；按对象和信号保留草稿、图文选项、还原、过期 / 失败恢复 |
| 左右分区与自适应 | 场景内 `style.css`、`ConfigurationExample.vue` 与 core `PanelResizeHandle/` | 按实际容器重排，分界线键盘操作，窄屏任务顺序；重排不重建草稿 |
| 状态与执行边界 | `usePointWorkspace.ts`、`useInteractionExamples.ts`、`model.ts` | 对象身份与已应用数据同源、草稿隔离、创建草稿保留；请求序号与结果签名防止错归属 |

开发路由为 `/interaction-examples`，独立预览入口为 `/src/views/interaction-examples/preview.html`。场景使用 core 与其声明依赖，数据为当前会话本地样例。它们证明交互与组合方式，不证明真实 API、权限或生产执行器已接通。

`PreviewRoot.vue` 只负责独立入口的主题 Provider、语言与外层留白；嵌入平台沿实际应用主题和壳层。独立入口不加载账号 / 项目运行时偏好和完整导航，其截图不能代替目标平台视觉验收，迁移时按 [宿主契约](shared-interaction-contracts.md#原型进入平台统一宿主契约) 核对。

## 能力入口

- core 总索引：`jetlinks-web-core/src/README.md`
- 组件：`src/components/README.md` → `src/components/index.ts` → 候选源码
- hooks、utils、store：对应分类 README（若有）与 `index.ts`
- 表达式：`src/components/Expression/index.ts` 及其编辑、反显、试算契约
- 公共选项与编辑：`src/components/SelectOption/`、`src/components/Editable/`
- 页面索引：`src/views/README.md`

共享基础包与目标版本的核验仍按 [组件事实源](component-source-rules.md)。能力目录存在不等于根入口具名导出，示例内部相对导入也不能当成业务调用的公共路径。

## 当前业务与跨模块边界

实现时核对当前任务的真实接口、路由、权限、i18n 和公开入口；这属于目标业务事实，不把其他模块的页面当成必读参考。

确需跨模块协作时核验当前工作区已提供的稳定导出或注册契约，例如 `src/utils/module-registry.ts`。只消费已声明的资源，保持公共入口和私有实现的边界。

## 定向检索

```bash
rg --files jetlinks-web-core/src/views/interaction-examples
rg -n "SelectOption|Editable|PanelResizeHandle" jetlinks-web-core/src/components/index.ts
rg -n "MathExpressionEditor|MathExpressionView|ExpressionTrial" jetlinks-web-core/src/components/Expression/index.ts
```

目标版本尚无这些场景时说明版本差异，并按当前 core 的真实契约实施；不假定示例已安装。
