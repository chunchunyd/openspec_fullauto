# Delta for Agent Tasks

## ADDED Requirements

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

