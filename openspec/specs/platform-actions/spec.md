# Platform Actions Specification

## Purpose

本规格定义“能干”项目首期平台动作契约的当前行为真相源。

首期 platform actions 能力聚焦于：

- 为 runtime 与平台能力调用提供稳定动作边界
- 区分动作契约、事件契约与内部异步 transport
- 定义统一请求/响应 envelope
- 定义统一错误边界

## Requirements

### Requirement: 系统必须提供独立于事件和内部 job 的平台动作契约

系统必须提供独立于平台事件和内部异步 job payload 的平台动作契约，供 runtime 或其他受控调用方请求平台能力。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

平台动作可以在内部映射到同步 service 调用、异步 job 或其他执行路径，但这些内部 transport 不得反向成为上层稳定能力契约。


#### Scenario: runtime 请求平台能力

- WHEN runtime 需要读取知识、写入草稿、追加审计或调用其他平台能力
- THEN 它必须通过平台动作契约表达该请求
- AND 不应把内部 job payload、数据库调用或 app-local service 方法签名当作稳定调用边界

#### Scenario: 平台内部替换执行路径

- WHEN 某个平台动作从同步实现切换为异步 job 或其他内部 transport
- THEN 上层动作契约应继续保持稳定
- AND 调用方不应因为内部 transport 变化而重写动作语义

### Requirement: 系统必须定义统一的动作请求与响应 envelope

系统必须为平台动作定义统一的最小请求与响应 envelope。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期动作请求至少应包含：

- `actionName`
- `actionVersion`
- `correlationId`
- `idempotencyKey`
- `actor`
- `source`
- `payload`

首期动作响应至少应包含：

- `actionName`
- `status`
- `correlationId`
- `result` 或 `error`


#### Scenario: 构造一个平台动作请求

- WHEN runtime 或其他受控调用方发起平台动作请求
- THEN 该请求必须包含统一 envelope 字段
- AND 平台必须能够基于这些字段进行追踪、鉴权或幂等处理

#### Scenario: 返回动作处理结果

- WHEN 平台完成一次动作处理
- THEN 它必须返回统一响应 envelope
- AND 调用方不得依赖隐式的 app-local 返回结构推断结果

### Requirement: 系统必须提供统一的动作错误边界

系统必须为平台动作提供统一的错误边界，而不是让每个动作各自发明难以对齐的错误格式。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持以下错误类型中的全部或核心子集：

- 校验失败
- 权限拒绝
- 状态冲突
- 上游不可用
- 超时
- 内部错误


#### Scenario: 动作命中权限限制

- WHEN 某个平台动作因权限或策略限制无法执行
- THEN 平台必须返回统一的错误结构
- AND 调用方必须能够据此识别这是受控拒绝而不是未知崩溃

#### Scenario: 动作上游依赖异常

- WHEN 某个平台动作依赖的上游能力暂时不可用
- THEN 平台必须返回统一的上游或超时错误结果
- AND 不应把这类失败伪装为业务成功

### Requirement: 系统必须提供首期最小 smoke action

系统必须提供至少一个可用于连通性与集成验收的最小平台动作。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期最小 smoke action 至少应支持等价于 `system.ping` 的能力。


#### Scenario: 校验平台动作链路可用

- WHEN 平台或 runtime 需要验证动作链路是否可用
- THEN 系统必须支持发起一个最小 smoke action
- AND 调用方必须能够获得明确成功或失败结果
