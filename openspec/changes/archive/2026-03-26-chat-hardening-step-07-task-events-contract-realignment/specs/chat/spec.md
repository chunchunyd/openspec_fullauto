# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须让 chat task events 契约与真实返回保持一致

系统必须让 chat task events 的对外契约、文档和导出结果与真实返回结构保持一致，而不是继续暴露过时的字段命名或不完整的状态枚举。 The system MUST keep the chat task-events contract aligned with the actual response shape and state semantics.

#### Scenario: 文档化增量与完成事件载荷

- WHEN 调用方读取 chat task events 契约或 OpenAPI 文档
- THEN 它必须能够看到与真实返回一致的 `content.delta`、`content.completed` 或等价正式命名
- AND 不得被旧的 `reply.*` 命名误导

#### Scenario: 文档化状态与进度语义

- WHEN 调用方依据 task events 契约实现状态解析
- THEN 契约必须准确表达实际可能出现的事件状态、进度字段和未知态兜底
- AND 不得省略已经在服务真实返回中存在的正式状态值

