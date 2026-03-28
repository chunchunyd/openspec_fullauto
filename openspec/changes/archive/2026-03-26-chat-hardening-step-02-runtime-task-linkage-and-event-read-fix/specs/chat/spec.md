# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须通过受控映射读取 chat 对应的 runtime 任务结果

系统必须通过平台 task 与 runtime task 之间的受控映射读取 chat 事件结果，而不是假设两侧 task 标识天然相同。 The system MUST read chat runtime results through a controlled platform-task-to-runtime-task mapping.

#### Scenario: 发送消息后读取任务事件

- WHEN 平台已经为一条聊天用户消息创建 task 并成功派发到 runtime
- THEN 后续事件读取必须通过该平台 task 对应的 runtime task 关联访问真实结果
- AND 不得依赖“平台 task id 与 runtime task id 恰好相同”的隐式假设

#### Scenario: runtime 映射缺失或失效

- WHEN 平台 task 尚未持有可用的 runtime task 关联，或其关联已经失效
- THEN 系统必须返回受控错误或受控未就绪结果
- AND 不得把错误映射静默伪装成正常的空事件列表

