# JetLinks Web Core 能力文档读取规则

本文件规定 `jetlinks-web` 如何消费 `cloud.jetlinks/ui/jetlinks-web-core/src` 下的轻量能力说明。文档用于降低发现成本，不替代真实导出、源码、依赖版本和生产用法核验。

## 何时读取

当任务涉及 `jetlinks-web-core` 的组件、hooks、utils、store 或 core 页面时，先读取 core 总索引（若目标 workspace 已提供）：

```text
jetlinks-web-core/src/README.md
```

再按任务类型读取一个分类索引，不要默认全文加载所有能力文档：

| 任务 | 分类索引 |
| --- | --- |
| 组件、页面壳、交互封装 | `jetlinks-web-core/src/components/README.md` |
| Hook、响应式逻辑、订阅 | `jetlinks-web-core/src/hooks/README.md` |
| 工具函数、查询编码、运行时 | `jetlinks-web-core/src/utils/README.md` |
| Pinia、跨页面共享状态 | `jetlinks-web-core/src/store/README.md` |
| core 页面或页面族 | `jetlinks-web-core/src/views/README.md` |

如果分类索引推荐了单项 README，再只打开 1～3 个与当前场景最匹配的说明；文档不存在时回退到对应 `index.ts`、源码和相邻生产用法，不把缺少文档误判为缺少能力。

## 核验顺序

```text
core 总索引
  → 分类索引
    → 单项 README（如有）
      → 分类 index.ts / 根导出
        → 能力源码
          → 相邻生产用法与目标项目版本
```

- 组件必须区分目录名、全局注册名、具名导出和深层路径；优先核验 `src/components/index.ts`。
- Hook、utils 和 store 必须核验各自分类 `index.ts`；文件存在、被内部使用或有 README，都不能单独证明根入口可导入。
- 页面必须核验真实路由入口、API、权限、Store/Hook 和回跳关系；页面 README 只提供导航和语义摘要。
- 文档与源码、导出或生产代码冲突时，以当前 workspace 的真实代码和目标版本为准，并在结果中说明冲突。

## 文档作者约定

新增公共能力时，在对应分类索引增加一行；复杂能力再在源码旁增加单项 README。说明至少包含：

- 解决的问题、适用场景和明确的不适用场景；
- 实际导入路径，以及根入口/全局注册/深层路径事实；
- 关键参数、返回值、事件或状态契约；
- 请求、订阅、路由、Store、localStorage 或环境变量等副作用；
- 最小调用示例和一个生产用法定位。

页面说明额外写目标用户、第一任务、成功标准、入口/路由、真实数据来源、权限和状态边界。不要把临时排查记录、未确认设计或测试流水写入能力索引。

## 与业务模块文档的边界

- Core 索引只描述跨模块稳定能力和 core 页面；单模块业务能力仍以 `modules/<module>-ui` 自己的 README、入口和生产代码为准。
- 相似页面可以作为交互参考，但不能因为 core 页面或文档存在就复制其 API、字段、权限或页面壳层。
- 跨模块能力优先核验公开导出、注册中心或稳定扩展点，不直接深层引用其他模块私有实现。
