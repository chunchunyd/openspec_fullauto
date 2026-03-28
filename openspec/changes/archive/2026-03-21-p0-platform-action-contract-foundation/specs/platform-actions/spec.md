# Delta for Platform Actions

## ADDED Requirements

### Requirement: 系统必须提供独立于内部 transport 的平台动作契约

系统必须提供独立于内部异步 transport、Nest DTO 和临时 CLI 参数格式的平台动作契约，供当前后端、CLI adapter 和未来原生平台内核围绕同一能力边界演进。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期该契约至少应包括：

- 动作名称
- 请求 envelope
- 响应 envelope
- 错误边界
- 关联元数据


#### Scenario: Adapter 请求平台能力

- WHEN Agent 或 CLI adapter 需要请求平台执行某个能力
- THEN 它必须通过平台动作契约发起请求
- AND 该请求不得直接等同于某个内部 BullMQ job 或某个 app-local DTO

#### Scenario: 平台动作契约演进 transport

- WHEN 平台动作在不同阶段采用不同 transport 实现
- THEN 契约边界必须保持稳定
- AND 具体 transport 细节不得反向污染平台动作定义

### Requirement: 系统必须由平台侧执行状态变更与权限校验

系统必须由平台侧动作执行真实的状态变更、权限校验和业务约束，而不是让 Agent 或 adapter 直接操作数据库或内部服务。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: Adapter 触发状态变更

- WHEN Agent 或 adapter 触发需要写入平台状态的动作
- THEN 平台必须通过正式动作执行该变更
- AND 动作执行中必须保留平台侧的权限、校验和状态机边界

#### Scenario: Agent 编排业务能力

- WHEN Agent 需要组合多个平台能力完成编排
- THEN 它可以决定何时请求某个动作
- AND 它不得绕过平台动作边界直接碰平台内部持久化层

### Requirement: 系统必须为应用层提供 AI runtime 反腐入口

系统必须为应用层提供统一的 AI runtime / adapter 反腐入口，避免业务模块直接依赖底层模型 client、内部 queue 或临时 adapter 细节。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 业务模块请求 AI 协作能力

- WHEN `auth`、`agents`、`chat`、`content` 等业务模块需要请求 AI / Agent 协作能力
- THEN 它们必须通过统一的 AI runtime 入口发起请求
- AND 不应在业务模块中长期散落底层 adapter、Bull queue 或模型接线细节

### Requirement: 系统必须区分平台动作契约与内部 job 契约

系统必须区分面向 adapter / future kernel 的平台动作契约与面向内部异步 transport 的 job 契约，避免两者混成同一层。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 平台动作内部异步执行

- WHEN 某个平台动作在当前实现中需要通过内部队列异步完成
- THEN 平台可以在内部将该动作落成 job
- AND 平台对外稳定能力边界仍必须保持为平台动作契约，而不是暴露内部 job 契约
