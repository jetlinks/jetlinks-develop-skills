# JetLinks 通用代码规范

本文件用于约束 JetLinks 系项目中的基础编码风格，避免智能体在陌生脚手架里凭记忆生成“看起来能跑、但不符合本仓库习惯”的代码。

## 核心原则

1. 先发现，再实现
   - 先看相邻代码、父子模块结构、现有配置和依赖，再写代码。
   - 不凭记忆假设模块名、包路径、版本号、资源路径。

2. 跟随当前模块风格
   - 响应式或阻塞式、控制器基类、服务基类、实体基类、权限注解、OpenAPI 注解，都以目标模块现状为准。
   - 如果同一模块已经有稳定风格，不要引入第二套写法。

3. 优先复用现有抽象
   - 先复用现有 CRUD 基类、查询抽象、事件机制、命令边界、工具类。
   - 不为单个需求新建平行框架。
   - 通用能力被某个具体场景暴露问题时，优先修正通用契约、扩展点、适配层或默认策略，不为该场景写硬编码特调分支。

4. 保持最小实现
   - 只实现用户明确要求的能力。
   - 不额外生成样板接口、演示字段、假设性的扩展点。
   - 最小实现不等于单场景打补丁；如果能力本身会被多个模块、租户、协议、页面或任务复用，改动应覆盖同类问题的共同根因。

5. 可读性优先于长链压缩
   - 链式调用只适合表达同一层次的连续操作。
   - 当一条链同时包含参数整理、权限判断、查询、转换、持久化、副作用或错误处理等多个阶段时，拆成命名方法或局部变量。
   - 命名步骤应让读者和智能体都能快速看出业务意图，不用从十几行链式调用里反推流程。
   - 注释也是可读性的一部分：复杂业务和非显而易见的边界要有短注释，但不要用注释重复代码表层含义。

6. 命名必须与现有代码一致
   - 类名、包名、资源路径、权限 ID、动作 ID、service id 的命名优先复用相邻模块模式。
   - 若当前仓库缺少样例，才采用稳定、可解释的最小命名。

7. 区分事实与默认决策
   - 当前工作区已有代码、依赖、目录结构，属于事实。
   - 在空脚手架中做出的最小补全，只能视为默认决策，不能伪装成仓库既有约定。

8. 根因优先，禁用奇技淫巧
   - 当工具、SDK、框架或现有 API 不直接满足需求（无法访问方法、序列化报错、响应式/阻塞不匹配、类型/泛型不兼容、第三方行为不符合预期、异常体系缺口等）时，必须从根本上解决：官方扩展点 → 相邻模块封装 → 依赖版本/选择 → 告知用户与替代方案。
   - 当问题发生在通用功能上，先判断失败是否代表同类场景都会受影响；若是，修通用入口、数据模型、策略接口、默认实现或测试矩阵，不把场景名、产品 ID、模块 ID、租户 ID、页面路由等写成特殊判断。
   - 禁止用反射 + `setAccessible`、`Unsafe`、改可见性、复制粘贴第三方源码、字节码注入、monkey patch、改类加载器、把代码挪进库的包路径下骗封装、`catch(Exception e){}` 静默吞、`e.printStackTrace()` 当处理、`@SuppressWarnings` 大范围压制告警、注释掉失败测试等手法绕过问题。
   - 任何上述路径如果是唯一可行方案，必须先告知用户限制、风险与建议，取得确认后再使用，并在代码注释或交付说明中留痕。
   - 详细场景见 [`root-cause-and-no-hack-rules.md`](root-cause-and-no-hack-rules.md)。

9. 发布边界优先，避免无效兼容
   - 同一个未发布 PR 内的早期实现、草稿字段、临时 DTO、旧测试期望或旧调用方，不构成历史兼容负担。
   - 遇到同 PR 内逻辑调整，优先收敛成单一最佳实践实现，并同步更新调用方、测试、fixture、文档和示例。
   - 只有旧行为已合入主线、发布生产、产生持久化数据、被外部系统 / 用户保存配置 / 链接 / 查询依赖，或用户明确要求保留时，才写兼容、迁移或过渡逻辑。
   - 拿不准是否已有发布或外部依赖时，先问用户确认，不要为了“保险”保留旧分支、旧参数别名、双 DTO 解析、临时 feature flag 或旧行为测试。

10. 关键业务链路要可追踪
   - 新增或修改关键后端业务流程时，主动判断是否需要手动链路追踪埋点。
   - 使用平台 `TraceHolder` / `MonoTracer` / `FluxTracer`，记录稳定 span 名称和必要业务属性，不自造追踪封装。
   - 详细规则见 [`tracing.md`](tracing.md)。

11. 常驻能力要便于运维定位
   - 常驻内存任务、缓存、队列、buffer、重试池、会话 / 连接 / 订阅管理器等能力，主动判断是否需要提供 MBean。
   - MBean 以辅助运维排障为目标，暴露统计、状态和安全内部操作，例如刷新缓存、flush、compact、手动重试、重置统计。
   - 详细规则见 [`mbean-observability.md`](mbean-observability.md)。

12. 注释要帮助人和模型理解代码
   - 不能完全不写注释；关键业务规则、兼容原因、并发保护、生命周期、权限、安全、TraceHolder 和 MBean 边界需要短注释。
   - 类注释和 SPI 接口方法注释必须完整，写清职责、调用时机、参数、返回、错误、副作用和实现约束；必要时补真实 `@since` 和指向订阅相关类型 / 参考实现的 `@see`。
   - 注释解释“为什么”和“边界”，不要逐行解释“代码做了什么”。
   - 详细规则见 [`code-comments.md`](code-comments.md)。

## 常见落地要求

### 导入与注解

- 先复制同类文件的导入家族，再替换业务类型。
- 高风险导入优先确认：
  - `javax` / `jakarta`
  - Swagger / OpenAPI
  - 事务相关注解
  - CRUD 基类和服务基类包路径

### 命名与资源标识

- Controller 路径、资源权限 ID、服务名尽量一一对应。
- 不臆造 command id、topic、事件名、support id。
- 没有明确业务需求时，不新增细粒度动作权限。

### 常用工具类

- 对集合、Map、数组和对象的判空、默认值处理等常用操作，在当前模块已引入 Apache Commons 或相邻实现已使用时，优先复用 `ObjectUtils`、`ArrayUtils`、`CollectionUtils`、`MapUtils` 等相关工具类。
- 不把 `org.apache.commons.lang3.StringUtils` 整类视为禁用；按当前 Commons Lang Javadoc 的 deprecated 状态决策。禁止的是已废弃方法和会继续扩散废弃 API 的新调用，不是仍有效的 null-safe predicate。
- 字符串比较、前后缀、包含、索引 / 查找、普通字符串替换 / 移除等 Commons Lang 操作，当前依赖提供 `org.apache.commons.lang3.Strings` 时，必须按大小写语义选择 `Strings.CS` 或 `Strings.CI`。
- 禁止新增或保留本次触达代码中的废弃 `StringUtils` 方法：`startsWith`、`endsWith`、`contains`、`equals`、`compare`、`indexOf`、`lastIndexOf`、`replace`、`remove`、`appendIfMissing`、`prependIfMissing`、`defaultString(str, defaultValue)` 及对应 `*IgnoreCase` / `*Any` / `*Once` / `*Start` / `*End` 变体；例如使用 `Strings.CS.startsWith(str, prefix)`、`Strings.CI.contains(str, keyword)`、`Strings.CI.equals(a, b)`，使用 `Objects.toString(value, defaultValue)` 替代带默认值的 `defaultString`。
- 正则替换 / 移除不要套用 `Strings.CS` / `Strings.CI`，按当前 Commons Lang 版本和相邻代码选择 `RegExUtils` 等非废弃 API。
- `StringUtils.isEmpty`、`isNotEmpty`、`isBlank`、`isNotBlank`、`defaultIfEmpty`、`defaultIfBlank`、`firstNonEmpty`、`firstNonBlank`、`defaultString(str)` 等未废弃 null-safe 方法可以在模块已有 Commons Lang 风格、入参可能为 `null`、且能减少重复样板判断时使用。
- 接收方已确认非空时优先用 JDK `String.isEmpty()`、`isBlank()`、`strip()`、`trim()`；Spring 场景可按本地风格使用 `org.springframework.util.StringUtils.hasText` / `hasLength`，但要避免与 Apache Commons `StringUtils` 导入混淆。
- 避免把禁用废弃 `StringUtils` 方法理解成鼓励到处手写重复样板。若同一类里多次需要 null-safe 字符串判断，优先复用未废弃工具方法、本地统一工具类，或提取命名清晰的私有 helper。
- 如果 commons-lang3 版本尚未提供 `Strings`，不要为单个 helper 私自升级依赖；先跟随已存在的非废弃本地方案，或在交付说明中明确版本约束和无法替换的原因。

### 链式调用可读性

- 一条链应尽量只表达一个语义层次，例如构造查询、执行异步步骤、转换 DTO、发布副作用，不要全部塞在同一条链里。
- 链路超过读者需要反复回看才能理解时，按业务阶段拆分：`buildXxxQuery(...)`、`assertXxxPermission(...)`、`toXxxView(...)`、`publishXxxEvent(...)`。
- 拆分不等于引入大抽象；优先使用私有方法、局部变量或已有 helper，保持调用处像流程目录一样可读。
- 不为了减少行数牺牲可读性，也不把复杂业务逻辑藏进 lambda、匿名内部类或连续 fluent 调用。
- 当链式 DSL 本身是领域语言时，保留 DSL，但把复杂条件、嵌套分组、权限注入、结果装配拆成命名步骤。

### 注释规范

- 复杂业务规则、历史兼容、并发 / 幂等保护、生命周期、资源释放、安全脱敏、TraceHolder 属性选择、MBean 操作上限等，必须写短注释说明原因或边界。
- 对外类、接口、抽象类、枚举、Command、Event、Codec、Provider、MBean 必须写完整类注释；SPI / 扩展点方法必须写完整方法注释。
- SPI 类和方法新增 / 变更公共契约时，按模块既有格式补 `@since`；涉及订阅、事件、Provider、Codec、Listener、默认实现或参考实现时，用 `@see` 指向最关键的相关类型。版本拿不准时先问用户，不编造。
- 简单赋值、DTO 搬运、直观方法调用、普通判空、getter / setter 不写注释。
- 临时兼容或兜底逻辑必须写明触发原因、移除条件或关联事项，避免以后无法判断能否删除。
- 修改代码时同步更新或删除过期注释。

### Java Stream 与过程式代码取舍

- 业务流程编排、协议解析、状态机流转、复杂校验优先过程式代码，用中间变量和小函数表达步骤。
- 集合过滤、DTO 转换、简单分组聚合、纯数据变换可以使用 Stream，但链路只承载纯函数。
- Stream 链中不要做权限判断、缓存更新、数据库 / 远程调用、事件发布、异常流程编排或外部变量修改。
- 避免用 `peek(...)` 承载业务副作用；需要副作用时，用显式循环或拆到命名方法里。
- 给关键中间结果命名，例如 `onlineDevices`、`alarmDevices`、`result`，比把所有判断折叠进一条 stream 链更容易审查和调试。

示例：

```java
List<Device> onlineDevices = filterOnlineDevices(devices);
List<Device> alarmDevices = filterAlarmDevices(onlineDevices);
List<DeviceDTO> result = convertToDTO(alarmDevices);
```

复杂判断抽成小函数：

```java
private boolean shouldTriggerAlarm(Device device, AlarmRule rule) {
    if (!device.isOnline()) {
        return false;
    }
    if (!rule.isEnabled()) {
        return false;
    }
    return device.getTemperature() > rule.getThreshold();
}
```

### 缓存与超时

- 如果需求包含超时缓存、写入后过期、读取后过期或基于时间窗口的本地缓存，优先复用现有缓存抽象，不要手写 `Map + Mono.cache + 定时清理` 一类临时方案。
- 需要统一缓存抽象或响应式访问时，必须优先使用 `org.hswebframework.web.cache.ReactiveCache<E>`。
- 需要本地 TTL / size 控制等 Caffeine 能力时，必须使用 `com.github.benmanes.caffeine.cache.Caffeine<K, V>` 构建缓存。
- 只有在相邻模块已经存在更明确的缓存封装时，才沿用本地封装；不要新造第三套超时缓存实现。
- 缓存如果是常驻能力或排障关键路径，设计时同步考虑 MBean：命中 / 未命中、大小、最后刷新时间、最近错误、刷新 / 清理 / 重载操作，以及敏感信息和返回数量边界。

### i18n

- 只有当前模块已存在 i18n 目录或明显使用 i18n 约定时，才补国际化资源。
- 对权限、动作、字段、枚举、错误消息的 i18n 跟随相邻模块做法。
- 用户可见异常优先复用当前模块支持的 `i18nCode` / message key 写法，不要在异常构造里直接写死中文或英文 message。
- 不为内部日志和调试信息补 i18n。

### 通用能力与场景特调

- 判断改动对象是否是通用能力：基础服务、公共组件、协议 / 命令 / 事件框架、CRUD 基类、权限模型、缓存 / 队列 / 调度、序列化、前端通用组件、工具类、模板或可配置策略。
- 如果是通用能力，某个场景的问题通常只是触发样例；先定位同类场景的共同根因，并在通用入口、抽象契约、策略接口、默认实现、配置模型或测试矩阵上解决。
- 禁止为了快速通过当前场景而写 `if (场景名 / productId / tenantId / route / moduleId / commandId)` 这类特调分支，除非业务明确要求该场景具有独立规则，并且规则已建模为配置、策略或可解释的业务条件。
- 真正局部的一次性需求可以局部实现，但必须说明它为什么不是通用能力缺口；不要把局部 workaround 混进公共层。
- 修改通用能力时，至少验证原始触发场景和一个同类代表场景；无法补自动化测试时，在交付说明中写清未覆盖的同类风险。

## 自检清单

- 是否先看了相邻代码而不是直接生成模板
- 是否复用了现有抽象
- 如果改的是通用能力，是否从共同根因修正，而不是为单个场景写特调分支
- 是否保持了目标模块的命名、注解和包结构
- 是否避免了过长链式调用；复杂流程是否按业务阶段拆成命名步骤
- 是否为复杂业务、兼容、并发、生命周期、安全、TraceHolder 或 MBean 边界写了必要短注释；是否避免无意义逐行注释
- 对外类注释和 SPI 接口方法注释是否完整，是否足以让实现者不读默认实现也能理解契约；SPI 是否在必要时补了真实 `@since` 和有助于定位订阅相关类 / 实现的 `@see`
- 是否对关键业务路径做了 TraceHolder 链路追踪判断；需要埋点时是否记录了稳定、非敏感的关键信息
- 是否对常驻任务、缓存、队列或重试池做了 MBean 运维可观测性判断；需要 MBean 时是否覆盖统计、监控和安全内部操作
- 是否避免了无根据的 i18n、权限和资源命名
- 如果写了兼容逻辑，是否有明确的已发布、持久化或外部依赖依据；同 PR 未发布中间形态是否已删除
- 是否明确区分了“现有事实”和“低上下文默认”
- 遇到能力缺口时，是否走的是“官方扩展点 → 相邻封装 → 依赖调整 → 告知用户”路径，而不是反射、改可见性、复制源码、monkey patch、静默吞异常或大面积压制告警
- 任何反射 / `Unsafe` / 改可见性 / 复制源码 / monkey patch / 字节码注入 / 在 i18n 模块硬编码 message / 响应式模块阻塞调用 / 新增不稳定依赖等高风险手法，是否已告知用户并取得确认
