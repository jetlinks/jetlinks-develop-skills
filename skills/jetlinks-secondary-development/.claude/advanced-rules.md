# Claude Code 使用建议

## 搜索优先级

1. 目标模块内的同类实现
2. 相邻业务模块中的相似实现
3. 聚合模块和父 `pom.xml`
4. `.prompt/*.md` 规则文件
5. 若模块路径是符号链接，再检查其真实目标路径

## 关键检查项

- 当前模块是响应式还是阻塞式
- 当前脚手架使用什么注解与导入家族
- 当前模块是否已有 i18n 约定
- 当前边界是否已有命令服务、事件或订阅模式
- 当前候选模块是否是软链接，以及真实代码是否在链接目标中

## 场景建议

### 新建模块

先看：
- 根 `pom.xml`
- 相邻聚合模块
- `.prompt/module-list.md`
- `.prompt/module-creation-rules.md`

### CRUD

先看：
- 目标模块内现有 Entity / Service / Controller
- `.prompt/common-crud-rules.md`
- 如查询复杂，再看 `.prompt/advanced-crud-rules.md`

### 跨边界调用

先看：
- 现有 command provider / proxy / support
- `.prompt/module-reference.md`
- `.prompt/cross-service-call-rules.md`

### 事件与订阅

先看：
- 现有 `@EventListener`
- 现有 `@Subscribe`
- 对应 `.prompt` 规则

## 结论

Claude Code 在该类项目中的最佳使用方式不是“背规则”，而是：

1. 用 `ai-prompt.md` 做总路由
2. 用 `.prompt/*.md` 做最小规则加载
3. 用当前工作区代码确认最终事实
