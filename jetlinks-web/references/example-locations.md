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
- 公共 hooks 参考：`jetlinks-web-core/src/hooks/**`
- 公共 utils 参考：`jetlinks-web-core/src/utils/**`
- 模块入口与注册参考：`modules/*-ui/index.ts`、`modules/*-ui/register.ts`

## 推荐检索命令

```bash
rg -n "ProSearch|j-pro-table|EditDialog|BatchImport" modules jetlinks-web-core
rg -n "useTabSaveSuccess|usePlatformContext|useRegistryOptions" modules jetlinks-web-core
rg -n "handleMenus|handleAuthMenu|paramsEncodeQuery|onlyMessage" modules jetlinks-web-core
rg --files modules | rg "views/.*/index.vue|api/|hooks/|store|register.ts|index.ts"
```

## 自检清单

- 是否至少参考了一个目标模块相邻实现。
- 是否核验了复用能力在当前工作区真实存在。
- 是否避免了脱离现有风格的“平地起楼”实现。
