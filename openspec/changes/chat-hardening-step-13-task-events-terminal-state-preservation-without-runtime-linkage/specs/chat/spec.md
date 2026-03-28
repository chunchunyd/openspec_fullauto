# Delta for Chat

## MODIFIED Requirements

### Requirement: 系统必须让 chat task events 契约与真实返回保持一致

系统必须让 chat task events 的对外契约、文档和导出结果与真实返回结构保持一致，并显式表达受控事件载荷、状态枚举以及未就绪 / 错误语义；当 `runtimeTaskId` 缺失时，响应仍必须保留平台 task 已知状态与完成态，而不是把所有结果都压成同一种 `UNKNOWN` 空页。 The system MUST keep chat task-events contracts aligned with actual payloads, controlled readiness/error outcomes, and the platform task's known state semantics even when runtime linkage is missing.

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
- **AND** 必须继续保留平台 task 已知的状态与完成态，而不是把所有结果伪装成相同的 `UNKNOWN` 普通空页

#### Scenario: dispatch 失败后读取 task events

- **WHEN** 某个平台 task 因 dispatch 失败已持久化为 `FAILED`，但该 task 从未建立 `runtimeTaskId`
- **THEN** task-events 的对外响应必须继续表达该 task 已失败且属于终态
- **AND** 调用方不得被 `RUNTIME_TASK_NOT_LINKED` 误导为“任务仍未完成”

#### Scenario: runtime 暂时不可读时读取 task events

- **WHEN** 平台 task 已存在有效 runtime task 关联，但 runtime 读取过程暂时失败
- **THEN** task-events 的对外响应必须显式表达这是受控的暂时性错误语义
- **AND** 不得只返回没有上下文的 `UNKNOWN` 与空事件数组
