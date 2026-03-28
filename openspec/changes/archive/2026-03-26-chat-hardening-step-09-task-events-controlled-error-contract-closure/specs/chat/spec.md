# Delta for Chat

## MODIFIED Requirements

### Requirement: 系统必须让 chat task events 契约与真实返回保持一致

系统必须让 chat task events 的对外契约、文档和导出结果与真实返回结构保持一致，并显式表达受控事件载荷、状态枚举以及未就绪 / 错误语义，而不是继续把差异化结果压扁成同一种 `UNKNOWN` 空页。 The system MUST keep the chat task-events contract aligned with actual response payloads, state semantics, and controlled readiness/error outcomes.

#### Scenario: 文档化增量与完成事件载荷

- **WHEN** 调用方读取 chat task events 契约或 OpenAPI 文档
- **THEN** 它必须能够看到与真实返回一致的 `content.delta`、`content.completed` 或等价正式命名
- **AND** 不得被旧的 `reply.*` 命名误导

#### Scenario: 文档化状态与进度语义

- **WHEN** 调用方依据 task events 契约实现状态解析
- **THEN** 契约必须准确表达实际可能出现的事件状态、进度字段和未知态兜底
- **AND** 不得省略已经在服务真实返回中存在的正式状态值

#### Scenario: runtime 映射缺失时读取 task events

- **WHEN** 平台 task 存在，但该 task 仍未持有可用的 runtime task 关联
- **THEN** task-events 的对外响应必须显式表达这是受控未就绪 / 映射缺失结果
- **AND** 不得把这类情况伪装成与“当前无新增事件”完全相同的普通成功空页

#### Scenario: runtime 暂时不可读时读取 task events

- **WHEN** 平台 task 已存在有效 runtime task 关联，但 runtime 读取过程暂时失败
- **THEN** task-events 的对外响应必须显式表达这是受控的暂时性错误语义
- **AND** 不得只返回没有上下文的 `UNKNOWN` 与空事件数组
