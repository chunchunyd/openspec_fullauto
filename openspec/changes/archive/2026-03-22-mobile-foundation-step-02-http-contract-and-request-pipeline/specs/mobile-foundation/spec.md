# Delta for Mobile Foundation

## ADDED Requirements

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
