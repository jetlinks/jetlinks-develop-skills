# JetLinks 开发规则库

开发相关任务请遵循以下流程：

1. 先阅读 `../ai-prompt.md`
2. 先判断任务类型，再读取最少规则文件
3. 先搜索当前工作区的真实实现，再生成代码
4. 如果模块目录是软链接，继续沿链接确认真实目标路径与代码内容

## 路由

- 不知道模块或目录落点：`.prompt/module-list.md`
- 不确定边界方式：`.prompt/module-reference.md`
- 不确定导入或注解：`.prompt/annotations-and-imports-reference.md`
- 新建模块：`.prompt/module-creation-rules.md`
- 标准 CRUD：`.prompt/common-crud-rules.md`
- 复杂 CRUD / 查询 / 批处理：`.prompt/advanced-crud-rules.md`
- 跨边界调用：`.prompt/cross-service-call-rules.md`
- 实时订阅：`.prompt/realtime-subscription-rules.md`
- 事件驱动：`.prompt/event-driven-rules.md`
- 国际化：`.prompt/i18n.md`

## 核心约束

- 不要把当前仓库的模块清单当成通用事实
- 不要忽略软链接进来的模块、组件或子工程
- 不要臆造包名、版本号、命令 ID、Topic 或资源路径
- 优先复用相邻代码的模式
- 只生成用户明确要求的内容
