# Delta for Agent Tasks

## ADDED Requirements

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
