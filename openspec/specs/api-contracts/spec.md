# API Contracts Specification

## Purpose

本规格定义“能干”项目首期 HTTP API 契约管理的当前行为真相源。

首期 API contract 能力聚焦于：

- 明确 API 服务是 HTTP contract 的真相源
- 明确 Agent runtime 的 gRPC / proto contract 与 HTTP contract 分层管理
- 明确共享契约产物的导出位置与用途
- 明确 `packages/api_contracts` 不承载服务端内部 DTO 与校验类
- 明确 `openapi-export` 的触发时机
- 避免前端依据口头约定或过期字段进行开发
## Requirements
### Requirement: API 服务必须是 HTTP contract 的真相源

系统必须将 API 服务中的接口定义与导出逻辑视为 HTTP contract 的真相源。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

共享契约产物、生成 client 和前端联调结果都必须从该真相源派生，而不是反向成为接口定义来源。

#### Scenario: 修改请求或响应契约

- WHEN 后端修改请求字段、响应字段、状态码、错误码、分页结构、Header 或等价 HTTP contract 内容
- THEN 该修改必须先在 API 真相源中完成
- AND 不得先在前端或共享产物中手工定义为事实标准

### Requirement: 系统必须区分 HTTP contract 与 Agent runtime transport contract

系统必须将对外 HTTP API contract 与 API 到 Agent runtime 之间的 transport contract 视为不同层次的契约。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `api-contracts` capability 只约束对外 HTTP contract 与其 OpenAPI 派生产物
- Agent runtime 的 task / event / error / proto contract 应由 `packages/agent_runtime_contracts` 或等价 runtime contract 真相源管理
- 两类契约可以在同一个 change 中同时演进，但不得混写为同一份真相源

#### Scenario: 修改 API 到 runtime 的 gRPC / proto 契约

- WHEN `apps/api` 与 Agent runtime 之间的 task、event、error 或 proto 契约发生变化
- THEN 这些变化必须先在 runtime contract 真相源中完成
- AND 不得把 `packages/api_contracts` 或 OpenAPI 产物误当作这类 transport contract 的真相源

#### Scenario: 仅修改对外 HTTP 契约

- WHEN 一个 change 只影响 API 对外 HTTP 字段或错误结构
- THEN 该 change 必须更新 API 真相源并执行 `openapi-export`
- AND 不应因为这类纯 HTTP contract 变化而默认改动 runtime gRPC / proto 契约

### Requirement: 共享 OpenAPI 产物必须作为派生契约对外分发

系统必须允许将导出的 OpenAPI 产物作为共享契约对外分发。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期共享契约产物应落在：

- `packages/api_contracts/openapi/openapi.json`

该文件可用于：

- front-end 字段对齐
- client 生成
- mock 或测试输入
- CI 契约检查

但它不得被当作手工维护的原始接口真相源。

#### Scenario: 前端读取共享契约

- WHEN `mobile` 或 `admin-web` 需要确认接口字段或错误结构
- THEN 它们可以读取 `packages/api_contracts/openapi/openapi.json`
- AND 必须将其视为 API 真相源导出的共享契约产物

### Requirement: 共享契约包不得承载服务端内部 DTO 与校验逻辑

系统必须将 `packages/api_contracts` 视为共享契约分发层，而不是 API 服务端运行时源码位置。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

`packages/api_contracts` 不得作为以下内容的长期落位：

- NestJS 控制器输入输出 DTO 的真相源
- 带有 `class-validator`、`class-transformer` 或等价运行时校验装饰器的服务端类
- 仅供 API 服务内部使用的 command、query、service input 或等价内部模型

如项目需要在共享契约包中暴露前端可消费的类型，这些类型也必须从 API 真相源导出或生成，而不得反向定义 API 契约。

#### Scenario: 服务端定义登录 DTO

- WHEN 后端需要定义短信登录、刷新 token、设备管理等接口的请求校验 DTO
- THEN 这些 DTO 必须定义在 `apps/api` 的服务端实现中
- AND 不得将 `packages/api_contracts/src/auth/dto` 或等价目录作为服务端 DTO 真相源

#### Scenario: 前端消费认证契约

- WHEN `mobile` 或 `admin-web` 需要消费 `auth` 相关字段定义
- THEN 它们应优先消费 `packages/api_contracts/openapi/openapi.json` 或由其生成的 client 与 types
- AND 不应直接依赖 API 服务内部 DTO 目录作为前端稳定契约

### Requirement: 影响 API contract 的 change 必须重新导出共享契约

系统必须在 API contract 发生变化时重新执行 `openapi-export`。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应将以下变化视为需要重新导出的 contract 变更：

- request 字段变化
- response 字段变化
- 错误结果变化
- 状态码变化
- Header 要求变化
- 分页或列表结构变化

#### Scenario: 后端接口字段发生变化

- WHEN 一个 change 修改了 API contract
- THEN 该 change 必须重新执行 `openapi-export`
- AND 更新后的共享契约产物必须进入仓库或等价交付链路

#### Scenario: 仅修改内部实现

- WHEN 一个 change 只修改内部实现而不影响 HTTP contract
- THEN 系统不要求仅因内部实现变化而重新导出共享契约

### Requirement: 前端不得以口头约定替代共享契约

系统必须避免前端仅依据临时讨论、口头约定或猜测字段进行稳定开发。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 前端等待后端契约稳定

- WHEN 一个前端改动依赖新的后端接口结构
- THEN 前端应以最近一次导出的共享契约作为字段依据
- AND 不应长期依赖未导出的临时字段约定推进正式接入

### Requirement: 共享契约必须服务生成与验证链路

系统必须允许共享契约进入生成与验证链路，而不仅作为只读文档。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持以下一种或多种用途：

- 生成 client
- 校验前后端字段一致性
- 作为 CI 契约检查输入

#### Scenario: 生成前端 client

- WHEN 项目需要为 `mobile` 或 `admin-web` 生成 API client
- THEN 生成过程应优先基于共享 OpenAPI 产物

#### Scenario: CI 验证契约更新

- WHEN CI 检查 API 契约是否与实现一致
- THEN CI 可以基于 `openapi-export` 与共享契约产物执行验证

### Requirement: API 服务必须提供可导出的 Swagger / OpenAPI 文档生成链路

系统必须在 API 服务中提供可导出的 Swagger / OpenAPI 文档生成链路，用于开发联调、共享契约导出和前后端字段对齐。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 本地开发查看 API 文档

- WHEN 开发者在本地启动 API 服务
- THEN 系统必须提供一个可访问的 Swagger 文档入口
- AND 开发者必须能够查看当前 HTTP contract 的主要结构

#### Scenario: 执行 openapi-export

- WHEN 开发者执行 `openapi-export`
- THEN 系统必须从 API 服务的 Swagger / OpenAPI 真相源生成 raw OpenAPI JSON
- AND 必须将共享契约产物更新到 `packages/api_contracts/openapi/openapi.json`

### Requirement: openapi-export 失败时不得产出冒充成功的坏契约文件

系统必须在 Swagger / OpenAPI 原始来源不可用时明确失败，而不是导出空文件、旧文件或残缺产物冒充成功结果。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 原始 OpenAPI JSON 来源不可用

- WHEN `openapi-export` 依赖的 Swagger / OpenAPI JSON 入口不可访问
- THEN 导出流程必须明确失败
- AND 不得把无效产物写成最新共享契约

### Requirement: 共享 OpenAPI 产物必须覆盖已交付的公开 HTTP 路径

系统必须让导出的共享 OpenAPI 产物覆盖当前已交付的公开 HTTP 路径与代表性契约结果，以便消费方能基于同一份派生产物联调。 The system MUST ensure the exported shared OpenAPI artifact covers delivered public HTTP paths and their representative contract shapes.

#### Scenario: 新增公开 HTTP 路径后执行 openapi-export

- WHEN API 服务新增或实质修改一条公开 HTTP 路径
- THEN 重新导出的共享 OpenAPI 产物必须包含该路径
- AND 结果中必须体现代表性的成功或错误契约结构

#### Scenario: 消费方读取共享契约

- WHEN `mobile`、`admin-web` 或其他消费方读取共享 OpenAPI 产物
- THEN 它们必须能够从该产物中看到当前已交付的公开路径
- AND 不应继续依赖缺失路径的旧契约推进正式接入

### Requirement: 共享 OpenAPI 产物必须表达 chat task events 的受控未就绪与错误语义

系统必须在共享 OpenAPI 产物中表达 chat task events 的受控未就绪与错误语义，而不是只导出事件列表和宽泛状态枚举。 The system MUST expose controlled chat task-events readiness and error semantics in the shared OpenAPI contract.

#### Scenario: task events 契约新增未就绪或错误字段

- **WHEN** `GET /chat/tasks/:taskId/events` 需要表达 runtime 未映射、runtime 暂不可读或等价受控语义
- **THEN** `openapi-export` 生成的共享契约必须导出这些字段或等价正式表达
- **AND** 不得让调用方只能通过源码猜测这些差异化结果

#### Scenario: 调用方依据共享契约实现轮询

- **WHEN** `mobile`、`admin-web` 或生成 client 读取 `packages/api_contracts/openapi/openapi.json`
- **THEN** 它们必须能够区分“当前无新增事件”和“受控未就绪 / 错误”的不同结果
- **AND** 不得被模糊的空数组与宽泛未知态误导

### Requirement: 共享 OpenAPI 产物必须为 chat 成功响应保留正确的标量类型与任务元数据字段

系统必须让共享 OpenAPI 产物正确表达 chat 成功响应中的标量字段与任务元数据字段，而不是导出成模糊对象或丢失关键追踪字段。 The system MUST preserve correct scalar types and task metadata fields for chat success responses in the shared OpenAPI contract.

#### Scenario: 导出 chat 成功响应的布尔标量

- **WHEN** API 服务导出 chat 相关成功响应的共享 OpenAPI 契约
- **THEN** `success` 这类布尔标量必须在共享契约中保持布尔类型
- **AND** 不得在导出结果中退化为 `type: object` 或其他错误标量表达

#### Scenario: 导出 chat 任务元数据字段

- **WHEN** chat 成功响应包含任务跟踪相关字段，例如 `runtimeTaskId`、`parentTaskId` 或等价失败信息
- **THEN** 共享契约必须显式导出这些字段
- **AND** 生成 client、测试夹具和验收链不得继续使用过期字段形状冒充当前契约

