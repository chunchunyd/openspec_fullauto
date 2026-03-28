# mobile-foundation Specification

## Purpose
TBD - created by archiving change mobile-foundation-step-01-app-shell-entry-boundary. Update Purpose after archive.
## Requirements
### Requirement: mobile 客户端必须提供项目自己的应用壳入口边界

mobile 客户端必须提供项目自己的应用壳入口边界，以替代 Flutter 默认 demo 入口并为后续 feature 提供受控宿主。 The mobile client MUST provide a project-owned app-shell entry boundary instead of relying on the default Flutter demo entrypoint.

#### Scenario: 通过默认入口启动应用

- WHEN 开发者或运行环境通过 `main.dart` 启动 mobile 应用
- THEN 客户端必须进入项目自己的 bootstrap 与 app shell 主线
- AND 不得继续把 Flutter 默认 counter demo 当作正式应用入口

#### Scenario: 通过环境入口启动应用

- WHEN 开发者或运行环境通过 `main_dev.dart`、`main_test.dart`、`main_staging.dart` 或 `main_prod.dart` 启动应用
- THEN 客户端必须进入与该入口对应的受控环境配置路径
- AND 不得静默回退到与入口不匹配的默认环境

### Requirement: mobile 客户端必须提供 public、auth 与 protected 的顶层路由空间

mobile 客户端必须提供 public、auth 与 protected 的顶层路由空间，以承载后续认证分流和受保护页面边界。 The mobile client MUST provide top-level public, auth, and protected route spaces for subsequent authentication and protected-page flows.

#### Scenario: 应用完成 bootstrap 后进入首个路由空间

- WHEN mobile 应用完成最小 bootstrap 并准备展示首个界面
- THEN 客户端必须进入 public、auth 或 protected 三类顶层空间之一
- AND 后续 feature 不得自行重新发明顶层宿主入口

#### Scenario: 路由未命中

- WHEN 客户端收到未知路由、非法入口或未命中的页面路径
- THEN 客户端必须进入统一 fallback
- AND 不得把 fallback 逻辑分散给各业务页面各自处理

### Requirement: mobile 客户端必须通过共享 HTTP contract 对齐 API 字段

mobile 客户端必须通过共享 HTTP contract 对齐 API 字段，以避免长期依赖口头约定、旧字段或服务端内部 DTO。 The mobile client MUST align API fields through the shared HTTP contract artifact instead of relying on drift-prone informal agreements.

#### Scenario: feature 需要确认接口字段

- WHEN mobile feature 需要确认请求字段、响应字段、状态码或错误结构
- THEN 客户端必须优先以共享 OpenAPI 产物或由其生成的 types / client 为依据
- AND 不得长期把服务端内部 DTO 或口头约定当作稳定契约

#### Scenario: API contract 发生变化

- WHEN 后端重新导出共享 OpenAPI 产物
- THEN mobile 客户端必须能够围绕该产物更新消费结果
- AND 不得继续默认沿用已经漂移的旧字段定义

### Requirement: mobile 客户端必须提供统一的请求管线与 transport 边界

mobile 客户端必须提供统一的请求管线与 transport 边界，以支撑后续 auth、内容、会话和设置等 feature 复用。 The mobile client MUST provide a unified request pipeline and transport boundary for subsequent feature reuse.

#### Scenario: feature 发起 API 请求

- WHEN 任意 mobile feature 发起受支持的 API 请求
- THEN 客户端必须通过统一请求管线进入底层 transport
- AND feature 不应长期各自维护 base URL、header 和 timeout 逻辑

#### Scenario: 请求失败

- WHEN 底层请求发生网络异常、超时、4xx 或 5xx
- THEN 客户端必须把结果映射为受控错误边界
- AND 页面不应长期直接依赖底层 HTTP 库原始错误格式进行分支判断

### Requirement: mobile 客户端必须提供统一的基础页面反馈原语

mobile 客户端必须提供统一的基础页面反馈原语，以避免各 feature 长期维护彼此漂移的 loading、empty、error 和 retry 语义。 The mobile client MUST provide shared page-feedback primitives for loading, empty, error, and retry states.

#### Scenario: 页面进入加载态

- WHEN 任意 mobile 页面进入受支持的加载态
- THEN 客户端必须能够复用统一的加载反馈组件
- AND 不得要求每个 feature 各自重新定义最小加载语义

#### Scenario: 页面进入空态或失败态

- WHEN 任意 mobile 页面进入空态、失败态或可重试状态
- THEN 客户端必须能够复用统一的反馈组件或等价页面壳
- AND 错误与重试入口不得长期分散在页面层各自实现

### Requirement: mobile 客户端必须对未处理异常提供应用级受控兜底

mobile 客户端必须对未处理异常提供应用级受控兜底，以避免最终用户直接面对原始堆栈、黑屏或不透明崩溃。 The mobile client MUST provide app-level controlled fallback behavior for unhandled exceptions.

#### Scenario: 运行时出现未处理异常

- WHEN Flutter 框架层、zone 或等价运行时路径出现未处理异常
- THEN mobile 客户端必须进入受控的异常兜底路径
- AND 不得直接把原始堆栈信息暴露给最终用户

#### Scenario: 页面需要把错误转为用户可理解结果

- WHEN 页面或公共组件需要把底层异常映射为用户可理解的反馈
- THEN mobile 客户端必须能够经过统一错误映射层处理
- AND 页面不应长期直接依赖底层异常类型进行分支判断

### Requirement: mobile 客户端必须通过受控存储抽象管理本地会话快照

mobile 客户端必须通过受控存储抽象管理本地会话快照，以避免页面层直接操作原始 secure storage、key 命名和清理语义。 The mobile client MUST manage local session snapshots through a controlled storage abstraction instead of exposing raw storage details to pages.

#### Scenario: 读写本地会话快照

- WHEN mobile 客户端需要读取、写入或清理本地会话快照
- THEN 这些操作必须通过统一的受控存储抽象完成
- AND 页面层不应长期直接操作原始本地存储 key

#### Scenario: 本地快照损坏

- WHEN 本地会话快照缺字段、格式损坏或明显非法
- THEN mobile 客户端必须以受控方式清理该快照
- AND 不得因为损坏快照直接导致页面层崩溃

### Requirement: mobile 客户端必须根据本地会话快照推导最小认证状态

mobile 客户端必须根据本地会话快照推导最小认证状态，以支撑后续 auth、协议 gating 和受保护路由分流。 The mobile client MUST derive minimal authentication state from the local session snapshot for downstream routing and request decisions.

#### Scenario: 启动时恢复本地状态

- WHEN mobile 应用启动并尝试恢复本地会话状态
- THEN 客户端必须能够把快照推导为受控的最小认证状态
- AND 该结果必须能够被路由层和请求层消费

#### Scenario: 本地不存在可用快照

- WHEN 本地不存在任何可用会话快照
- THEN mobile 客户端必须把当前状态视为未登录或等价 visitor 状态
- AND 不得误把用户直接导入受保护路由空间

### Requirement: mobile foundation 层必须提供最小结构化埋点钩子

mobile foundation 层必须提供最小结构化埋点钩子，以支持启动、路由分流、request 结果和本地会话恢复的统一事件接线。 The mobile foundation MUST provide minimal structured telemetry hooks for startup, routing, request results, and local session restoration.

#### Scenario: foundation 路径触发 hook

- WHEN 应用启动、路由分流、request 成功失败或 session 恢复发生
- THEN foundation 层必须能够通过统一接口发出最小结构化事件
- AND 不得要求各 feature 各自重新发明基础层 telemetry 入口

#### Scenario: 本地开发环境不接第三方供应商

- WHEN 当前环境未接入真实 analytics 供应商
- THEN foundation 层必须仍可通过 no-op、debug 或等价实现完成受控接线
- AND 基础层不得直接把真实供应商 SDK 视为强依赖

#### Scenario: foundation 事件包含敏感字段

- WHEN foundation hook 试图记录手机号、token 或 session snapshot 等敏感信息
- THEN 这些字段必须被省略、脱敏或映射为受控标识
- AND 不得直接输出完整敏感值

