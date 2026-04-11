# JetLinks 国际化使用指南

本指南用于在 JetLinks 项目中补充国际化能力。默认前提不是“所有模块都要补
i18n”，而是先确认当前模块已经存在这套约定，或用户明确要求新增。

## 第一原则

先判断当前模块是否真的使用 i18n：

- 是否存在 `src/main/resources/i18n/...`
- 是否已有 `messages_zh.properties`
- 是否已有 `messages_en.properties`
- 相邻模块是否对标签、枚举、权限、动作或错误消息做了本地化

如果当前模块没有这套约定，不要为了形式完整臆造一套新资源路径。只有用户明
确要求，或你正在创建一个明确需要多语言支持的新模块时，才引入新的 i18n 目
录。

## 典型目录结构

国际化资源通常位于模块自己的 `src/main/resources/i18n/{模块名}/` 目录下。

```text
项目根目录/
├── jetlinks-components/
│   └── {组件名}-component/
│       └── src/main/resources/
│           └── i18n/
│               └── {组件名}-component/
│                   ├── messages_zh.properties
│                   └── messages_en.properties
```

实际目录名以目标模块现状为准，不要把别的模块目录硬搬过来。

## 何时需要补 i18n

- 新增枚举显示文本，且前端会直接展示
- 新增 `@Resource` 权限 ID，且当前模块已有权限国际化
- 新增 `@ResourceAction` 或等价动作 ID，且当前模块已有动作国际化
- 新增用户可见错误、提示、告警、状态消息

通常不需要补 i18n 的内容：

- 纯内部日志
- 调试信息
- 只供开发者阅读的异常堆栈细节
- 当前模块完全没有国际化约定且用户未要求新增

## 资源文件约定

常见文件名：

- `messages_zh.properties`
- `messages_en.properties`

如果当前模块同时维护中英文资源，修改时尽量同步补齐两份。
如果当前模块只维护单语言，先跟随现有惯例，不要擅自扩成双语。

关于中文编码：

- 如果现有文件使用 `\uXXXX`，继续保持同样风格
- 如果现有文件已经直接使用 UTF-8 中文，继续沿用现有风格
- 不要在同一个模块里混用两套明显不同的编码习惯，除非项目本身已经如此

## Key 命名规范

普通消息建议沿用分层 key：

```text
{类型}.{模块}.{字段或语义}.{属性}
```

常见前缀：

- `error`: 错误消息
- `message`: 普通提示或状态消息
- `validation`: 校验消息

示例：

```properties
error.entity.not_found=对象不存在
message.operation.success=操作成功
validation.name.required=名称不能为空
```

关键要求：

- key 要和代码中的语义一一对应
- 同一模块内保持统一命名层级
- 不要把无关模块前缀混入当前模块

## Java 代码中的常见写法

导入：

```java
import org.hswebframework.web.i18n.LocaleUtils;
```

基本用法：

```java
String message = LocaleUtils.resolveMessage(
    "message.operation.success",
    "操作成功"
);
```

带参数：

```java
String message = LocaleUtils.resolveMessage(
    "message.relation.created",
    "对象 {0} 已关联到 {1}",
    sourceId, targetName
);
```

错误消息：

```java
String errorMessage = LocaleUtils.resolveMessage(
    "error.entity.not_found",
    "对象 {0} 不存在",
    entityId
);
```

异常如何抛出以目标模块现状为准，不要为了统一而强行切换异常模型。

## 响应式代码

响应式代码优先使用项目现有模式。

常见写法：

```java
return LocaleUtils.resolveMessageReactive("error.entity.not_found", entityId)
    .flatMap(errorMsg -> Mono.error(new NotFoundException(errorMsg)));
```

如果目标模块没有使用 `resolveMessageReactive(...)`，而是通过其他上下文方式处
理语言环境，优先跟随本地实现。

## 枚举国际化

如果枚举实现了 `I18nEnumDict`，key 命名应使用：

```text
{完整包名}.{枚举类名}.{枚举值名称}
```

示例：

```properties
org.jetlinks.example.device.DeviceState.ONLINE=在线
org.jetlinks.example.device.DeviceState.OFFLINE=离线
```

关键点：

- 包名、类名、枚举值大小写都必须完全匹配
- 找不到资源时，通常回退到枚举中的默认文本
- 新增枚举值时，资源文件也要同步补齐

## 最佳实践

- 始终在代码里提供默认值
- 只国际化用户可见内容
- 保持中英文 key 集合一致
- 保持同一术语在不同模块中的翻译一致
- 参考相邻模块的 key 风格、目录结构和资源编码
- 在提交前检查是否漏掉了英文或中文对应项

## 常见问题

### 为什么国际化没有生效

先检查：

- 文件路径是否在 `src/main/resources` 下
- 模块是否真的使用该 i18n 目录
- key 拼写是否与代码一致
- 资源文件命名是否与模块现状一致

### 是否需要手动传入 `LocaleUtils.current()`

通常不需要。优先使用：

```java
LocaleUtils.resolveMessage("message.operation.success", "操作成功")
```

只有当目标代码确实已经使用显式 `Locale` 重载时，才跟随现有模式。

### 如何验证新增 i18n 是否正确

- 切换语言后检查 UI 或接口返回文本
- 检查 `messages_zh.properties` 和 `messages_en.properties` 是否同步
- 检查 key 是否和权限、动作、枚举、字段、错误码一致
- 检查新增文本是否真的是用户可见内容
