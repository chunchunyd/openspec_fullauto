# Agent Tasks Specification

## Purpose

本规格定义“能干”项目首期统一 Agent 任务模型的当前行为真相源。

首期 Agent task 能力聚焦于：

- 为 Agent 协作请求提供统一任务记录
- 定义统一任务状态机
- 区分任务执行状态与业务结果状态
- 支持任务幂等与业务关联
## Requirements
### Requirement: 系统必须提供统一的 Agent 任务记录能力

系统必须为聊天、内容生成、Agent 训练和其他 Agent 协作请求提供统一任务记录能力，而不是让各业务模块长期维护各自漂移的任务模型。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期统一任务记录至少应包含：

- `taskId`
- `taskType`
- `status`
- `actorUserId`
- `targetAgentId`
- `bizType`
- `bizId`
- `inputPayload`
- `contextRefs`
- `idempotencyKey`
- `deadline`
- `priority`
- `createdAt`
- `updatedAt`

#### Scenario: 创建聊天任务

- WHEN 用户向 Agent 发起一次聊天协作请求
- THEN 系统必须创建一条统一 Agent 任务记录
- AND 该任务必须能够关联到对应会话、消息或等价业务对象

#### Scenario: 创建内容生成任务

- WHEN 用户触发一次内容生成请求
- THEN 系统必须创建一条统一 Agent 任务记录
- AND 该任务必须能够关联到对应帖子草稿、帖子结果或等价业务对象

### Requirement: 系统必须使用统一的 Agent 任务生命周期状态

系统必须使用统一的任务生命周期状态表达 Agent 协作请求的运行状态，而不是让 `chat`、`content` 或其他业务模块长期维护各自独立状态机。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期统一状态至少包括：

- `queued`
- `running`
- `waiting_tool`
- `streaming`
- `succeeded`
- `failed`
- `cancelled`

#### Scenario: 聊天任务开始流式返回

- WHEN 一次聊天任务已经开始回流渐进式结果
- THEN 该任务必须能够进入 `streaming` 状态
- AND 该状态不得用消息最终状态替代

#### Scenario: 任务执行失败

- WHEN 一次 Agent 协作请求因超时、异常、安全原因或策略拒绝而失败
- THEN 该任务必须进入 `failed` 状态
- AND 系统必须能够保留失败原因的最小可追踪信息

### Requirement: 系统必须支持任务与业务结果分层追踪

系统必须区分“任务当前执行状态”和“任务最终落成了什么业务结果”，不得将两者混为同一层语义。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 内容生成任务成功

- WHEN 一次内容生成任务成功完成
- THEN 任务必须进入 `succeeded` 状态
- AND 最终帖子仍可以分别处于草稿、待审核或已发布等业务状态

#### Scenario: 聊天任务成功

- WHEN 一次聊天任务成功完成
- THEN 任务必须进入 `succeeded` 状态
- AND 最终 Agent 回复必须作为消息结果被持久化，而不是仅由任务状态本身代表完整消息内容

### Requirement: 系统必须支持任务幂等与业务关联

系统必须支持通过幂等键和业务对象关联来避免重复创建同一次协作请求的任务记录。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 相同业务请求重复提交

- WHEN 同一次业务请求以相同幂等键重复提交
- THEN 系统必须能够识别其与既有任务的关联
- AND 不应无约束地创建多个重复任务记录

#### Scenario: 查询某个业务对象关联任务

- WHEN 平台需要查询一个会话、帖子或其他业务对象关联的 Agent 任务
- THEN 系统必须能够通过业务引用定位相关任务
- AND 任务记录不得成为与业务对象脱节的孤立状态

### Requirement: 系统必须让 chat 回复请求与统一 Agent task 锚点关联

系统必须让 chat 回复请求与统一 Agent task 锚点关联，以便 runtime 调用、流式事件、失败状态和重试语义共享同一条可追踪主线。 The system MUST associate chat reply requests with a unified agent task anchor.

#### Scenario: 为聊天用户消息创建任务

- WHEN 平台接受一条需要 Agent 回复的用户消息
- THEN 系统必须为该次回复创建或关联统一 Agent task 记录
- AND 该任务必须能够指向所属会话与触发它的用户消息

#### Scenario: 通过业务引用定位聊天任务

- WHEN 平台需要查询某条聊天用户消息对应的执行状态
- THEN 系统必须能够通过业务引用定位相关 Agent task
- AND 调用方不应依赖 runtime 私有 task 标识作为唯一业务锚点

### Requirement: 系统必须为 chat 回复过程保留 append-only 任务事件锚点或等价受控投影

系统必须为 chat 回复过程保留 append-only 任务事件锚点或等价受控投影，以便平台能够围绕统一 task 主线回放流式过程和最终结果。 The system MUST retain an append-only task event anchor or equivalent controlled projection for chat reply execution.

#### Scenario: 聊天任务产生流式事件

- WHEN 一次聊天任务在执行过程中产生渐进式回复事件
- THEN 系统必须能够围绕统一 task 记录这些事件或其等价受控投影
- AND 平台后续必须能够基于这些结果构建 chat 流式读取能力

#### Scenario: 读取聊天任务事件结果

- WHEN 平台需要读取某条聊天用户消息对应的执行过程
- THEN 系统必须能够通过统一 task 主线定位相关事件结果
- AND 调用方不应直接依赖 runtime 私有事件存储作为唯一读取来源

### Requirement: 系统必须为平台 AgentTask 保留 runtime 任务关联引用

系统必须为需要进入 runtime 的平台 `AgentTask` 保留 runtime 任务关联引用或等价受控映射，以支持后续状态查询、事件读取和结果投影。 The system MUST retain a runtime task reference or equivalent controlled mapping on platform agent tasks that dispatch to runtime.

#### Scenario: 平台 task 成功派发到 runtime

- WHEN 平台成功把一个聊天或等价协作任务派发到 runtime
- THEN 平台必须能够把对应 runtime task 标识或其等价映射保留下来
- AND 该关联不得只停留在瞬时响应中而不进入持久化主线

#### Scenario: 通过平台 task 查询 runtime 结果

- WHEN 平台需要围绕某个 `AgentTask` 读取 runtime 状态或事件
- THEN 平台必须能够通过该关联找到真实 runtime 任务
- AND 调用方不应自行拼接或猜测 runtime 私有标识

