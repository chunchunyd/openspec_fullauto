# Delta for API Contracts

## MODIFIED Requirements

### Requirement: 共享 OpenAPI 产物必须表达 chat task events 的受控未就绪与错误语义

系统必须在共享 OpenAPI 产物中表达 chat task events 的受控未就绪与错误语义，并允许这些错误字段与平台 task 已知状态 / 完成态一起出现，而不是只导出事件列表和宽泛状态枚举。 The system MUST expose controlled chat task-events readiness and error semantics in the shared OpenAPI contract without erasing the platform task's known state and completion semantics.

#### Scenario: task events 契约新增未就绪或错误字段

- **WHEN** `GET /chat/tasks/:taskId/events` 需要表达 runtime 未映射、runtime 暂不可读或等价受控语义
- **THEN** `openapi-export` 生成的共享契约必须导出这些字段或等价正式表达
- **AND** 不得让调用方只能通过源码猜测这些差异化结果

#### Scenario: 无 runtime 链接但平台 task 已知终态

- **WHEN** `GET /chat/tasks/:taskId/events` 返回 `RUNTIME_TASK_NOT_LINKED`，但平台 task 自身已经持久化为 `FAILED`、`CANCELLED` 或等价终态
- **THEN** 共享契约必须允许错误字段与正式 `status` / `isCompleted` 语义同时出现
- **AND** 不得迫使调用方把这类终态结果当成统一的 `UNKNOWN` 普通空页

#### Scenario: 调用方依据共享契约实现轮询

- **WHEN** `mobile`、`admin-web` 或生成 client 读取 `packages/api_contracts/openapi/openapi.json`
- **THEN** 它们必须能够区分“当前无新增事件”“受控未就绪 / 错误”以及“平台 task 已知终态但没有 runtime 链接”这几类不同结果
- **AND** 不得被模糊的空数组与宽泛未知态误导
