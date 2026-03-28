# Event Schema Specification

## Purpose

本规格定义“能干”项目首期平台事件契约的当前行为真相源。

首期事件 schema 能力聚焦于：

- 为任务回流和流式结果提供统一事件契约
- 定义统一事件 envelope
- 约束事件作为 append-only 通知的语义
- 为平台视图更新、分析和审计提供稳定上游输入

## Requirements

### Requirement: 系统必须提供独立于平台动作和内部 job 的事件契约

系统必须提供独立于平台动作请求和内部异步 job payload 的平台事件契约，供 API、runtime、analytics 和其他消费方围绕同一事件边界协作。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 任务执行过程需要回流结果

- WHEN 某次 Agent 任务的执行过程或执行结果需要被上游感知
- THEN 系统必须通过平台事件契约表达这些通知
- AND 不应直接把该通知等同为平台动作请求或内部后台 job payload

### Requirement: 系统必须定义统一的事件 envelope

系统必须为平台事件定义统一的最小 envelope 结构。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期事件 envelope 至少包含：

- `eventName`
- `eventVersion`
- `eventId`
- `occurredAt`
- `correlationId`
- `causationId`
- `payload`

在流式或任务相关事件中，还应支持：

- `taskId`
- `sequence`


#### Scenario: 构造任务状态变化事件

- WHEN 系统发出一条任务状态变化事件
- THEN 事件必须包含统一 envelope 字段
- AND 相关任务事件必须能够关联到对应 `taskId`

#### Scenario: 流式事件稳定排序

- WHEN 系统发出同一任务下的多条流式事件
- THEN 这些事件必须能够通过稳定顺序被消费
- AND 消费方不得依赖隐式时间碰撞处理消息乱序

### Requirement: 系统必须支持首期最小事件集

系统必须至少支持一组能够覆盖当前任务回流、聊天流式回流和内容结果回流的最小事件集。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期最小事件集至少包括：

- `task.updated`
- `message.delta`
- `message.completed`
- `post.draft.generated`


#### Scenario: 聊天流式回流

- WHEN 聊天任务开始渐进式返回内容
- THEN 系统必须能够发出 `message.delta` 或等价流式事件
- AND 流式事件必须能被稳定排序或稳定拼接

#### Scenario: 内容草稿生成完成

- WHEN 内容生成任务形成可消费的帖子草稿结果
- THEN 系统必须能够发出 `post.draft.generated` 或等价事件
- AND 事件必须能够关联对应任务和帖子结果

### Requirement: 系统必须将事件视为 append-only 通知

系统必须将平台事件视为 append-only 通知，而不是状态变更命令。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 消费平台事件

- WHEN 上游或其他系统消费一条平台事件
- THEN 它可以据此更新自己的视图、缓存或分析结果
- AND 它不得把事件本身当作绕过平台动作边界的状态修改命令

#### Scenario: 平台根据事件投影业务状态

- WHEN 平台需要根据任务事件更新会话、内容或其他业务对象的视图状态
- THEN 它必须由平台侧完成状态投影
- AND runtime 不得通过事件直接强制写入平台业务主状态
