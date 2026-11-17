# JetLinks 国际化使用指南

当你已经确认当前模块应该补 i18n，并且需要具体实现细节时，读取本文件。

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

## 资源文件约定

常见文件名：

- `messages_zh.properties`
- `messages_en.properties`

如果当前模块同时维护中英文资源，修改时尽量同步补齐两份。
如果当前模块只维护单语言，先跟随现有惯例，不要擅自扩成双语。

关于中文编码：

- 如果现有文件使用 `\uXXXX`，继续保持同样风格。
- 如果现有文件已经直接使用 UTF-8 中文，继续沿用现有风格。
- 不要在同一个模块里混用两套明显不同的编码习惯，除非项目本身已经如此。

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
error.entity.not_found=对象 {0} 不存在
message.operation.success=操作成功
validation.name.required=名称不能为空
```

关键要求：

- key 要和代码中的语义一一对应。
- 同一模块内保持统一命名层级。
- 不要把无关模块前缀混入当前模块。

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

用户可见异常：

- 先核验目标版本的异常继承链与构造器，保留 `i18nCode` 和真实格式化参数，由统一错误边界按请求语言解析。
- 当前 HSWeb `I18nSupportException(String code, Object... args)` 不接收独立 fallback；额外插入默认文案会改变参数位置。`BusinessException` 的业务 `code` 字段也不能当作默认文案槽位。
- 资源缺失策略沿框架支持的重载与错误返回契约处理，不要求所有 API 都额外接收默认文案。

避免写法：

- `throw new BusinessException("对象不存在")`
- `throw new IllegalArgumentException("名称不能为空")`

只有当目标模块的异常体系确实只能接收 `message` 时，才退回到：

1. 先用 `LocaleUtils.resolveMessage(...)` 或本地等价方式解析；
2. 再把解析后的结果传入旧异常模型。

这属于兼容旧模型，不是首选。

## 响应式代码

响应式代码优先使用项目现有模式。

对 `Mono.error(...)` 里的用户可见异常，同样优先传递带 `i18nCode` 的异常实例；不要先把 message 写死成字符串。

当前 HSWeb `NotFoundException` 经 `BusinessException` 继承 `I18nSupportException`，在用例确实要求 not-found 错误时可直接传 code / args：

```java
return Mono.error(new NotFoundException("error.entity.not_found", entityId));
```

不要先翻译再传给支持 code 的异常，避免丢失请求语言语义。只有旧边界确实仅接收文本时才提前解析；`LocaleUtils.resolveMessageReactive(String code, Object... args)` 从订阅上下文取语言，第二个参数不是 fallback。需要显式 fallback 时，核验并使用支持它的重载，例如在 `currentReactive()` 取得 Locale 后调用相应同步解析重载。

## 枚举国际化

如果枚举实现了 `I18nEnumDict` 且未覆盖 `getI18nCode()`，默认 key 使用：

```text
{完整包名}.{枚举类名}.{枚举值名称}
```

示例：

```properties
org.jetlinks.example.device.DeviceState.ONLINE=在线
org.jetlinks.example.device.DeviceState.OFFLINE=离线
```

关键点：

- 包名、类名、枚举值大小写都必须完全匹配。
- 找不到资源时，通常回退到枚举中的默认文本。
- 新增枚举值时，资源文件也要同步补齐。

## 最佳实践

- 仅在 API 明确支持时传默认文案，格式化参数须与资源占位符对应。
- 只国际化用户可见内容。
- 保持中英文 key 集合一致。
- 保持同一术语在不同模块中的翻译一致。
- 用户可见异常优先保留 `i18nCode` 与真实参数，不预先翻译为固定语言。
- 参考相邻模块的 key 风格、目录结构和资源编码。
- 在提交前检查是否漏掉了英文或中文对应项。

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

需要指定语言或传递请求上下文时，按目标重载显式传 Locale；是否有相邻样例不决定 API 能否使用。响应式链路不要用线程语言代替订阅上下文。

### 如何验证新增 i18n 是否正确

- 切换语言后检查 UI 或接口返回文本。
- 检查 `messages_zh.properties` 和 `messages_en.properties` 是否同步。
- 检查 key 是否和权限、动作、枚举、字段、错误码一致。
- 检查新增文本是否真的是用户可见内容。
