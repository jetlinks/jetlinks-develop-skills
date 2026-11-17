# JetLinks Web Example Locations

本文件用于快速定位可参考的真实实现，避免凭记忆实现前端能力。

## 示例查找原则

- 先找目标模块相邻页面，再找跨模块的公共实现。
- 先看最近维护、仍在使用的代码，不优先历史废弃目录。
- 发现多个实现时，优先跟随当前目标模块的写法。

## 常见查找入口（按工作区事实核验）

- 页面与流程参考：`modules/*-ui/views/**`
- 模块 API 参考：`modules/*-ui/api/**`
- 模块 hooks/store 参考：`modules/*-ui/hooks/**`、`modules/*-ui/store/**`
- 公共组件参考：`jetlinks-web-core/src/components/**`
- 公共组件导航：`jetlinks-web-core/src/components/README.md`
- 公共 hooks 参考：`jetlinks-web-core/src/hooks/**`
- 公共 hooks 导航：`jetlinks-web-core/src/hooks/README.md`
- 公共 utils 参考：`jetlinks-web-core/src/utils/**`
- 公共 utils 导航：`jetlinks-web-core/src/utils/README.md`
- 公共 store 参考与导航：`jetlinks-web-core/src/store/**`、`jetlinks-web-core/src/store/README.md`
- Core 页面入口与导航：`jetlinks-web-core/src/views/**`、`jetlinks-web-core/src/views/README.md`
- 模块入口与注册参考：`modules/*-ui/index.ts`、`modules/*-ui/register.ts`
- 模块注册中心参考：`jetlinks-web-core/src/utils/module-registry.ts`

## 跨模块能力调用约束

- 模块与模块之间需要复用 `api`、`hooks`、`components`、`utils` 等能力时，优先通过模块注册中心协作，不要直接跨模块深层 `import` 对方实现。
- 注册中心源码候选为 `jetlinks-web-core/src/utils/module-registry.ts`；常见公开别名是 `@jetlinks-web-core/utils/module-registry`，实际路径核对目标构建别名。
- 提供方先在 `modules/*-ui/register.ts` 或 `modules/*-ui/index.ts` 中统一注册资源，再由消费方通过 `moduleRegistry.getResource(moduleId, resourceType)`、`moduleRegistry.getResourceItem(moduleId, resourceType, resourceName)` 获取。
- 需要找真实示例时，优先查看模块入口里的 `moduleRegistry.register(name, registerSetting)`，再查看消费侧通过 `moduleRegistry.getResource(...)` 读取资源的页面或 hooks。
- 运行时模块资源沿已有注册中心协作；稳定共享类型、纯工具或 Core 公共契约可直接从公开入口导入，不为每个共享函数新增运行时注册。禁止直接导入其他业务模块私有实现。

## 推荐检索命令

```bash
rg -n "ProSearch|j-pro-table|EditDialog|BatchImport" modules jetlinks-web-core
rg -n "useTabSaveSuccess|usePlatformContext|useRegistryOptions" modules jetlinks-web-core
rg -n "handleMenus|handleAuthMenu|paramsEncodeQuery|onlyMessage" modules jetlinks-web-core
rg -n "moduleRegistry.register|moduleRegistry.getResource|moduleRegistry.getResourceItem" modules jetlinks-web-core
rg --files modules | rg "views/.*/index.vue|api/|hooks/|store|register.ts|index.ts"
```

## 自检清单

- 是否至少参考了一个目标模块相邻实现。
- 是否核验了复用能力在当前工作区真实存在。
- 如果是跨模块调用，是否先核验了 `module-registry` 中已有注册与读取模式，而不是直接跨模块引用 `api/hooks` 实现。
- 是否避免了脱离现有风格的“平地起楼”实现。
