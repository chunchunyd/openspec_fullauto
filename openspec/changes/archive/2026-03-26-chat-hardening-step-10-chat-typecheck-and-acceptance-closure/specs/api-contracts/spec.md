# Delta for API Contracts

## ADDED Requirements

### Requirement: 共享 OpenAPI 产物必须为 chat 成功响应保留正确的标量类型与任务元数据字段

系统必须让共享 OpenAPI 产物正确表达 chat 成功响应中的标量字段与任务元数据字段，而不是导出成模糊对象或丢失关键追踪字段。 The system MUST preserve correct scalar types and task metadata fields for chat success responses in the shared OpenAPI contract.

#### Scenario: 导出 chat 成功响应的布尔标量

- **WHEN** API 服务导出 chat 相关成功响应的共享 OpenAPI 契约
- **THEN** `success` 这类布尔标量必须在共享契约中保持布尔类型
- **AND** 不得在导出结果中退化为 `type: object` 或其他错误标量表达

#### Scenario: 导出 chat 任务元数据字段

- **WHEN** chat 成功响应包含任务跟踪相关字段，例如 `runtimeTaskId`、`parentTaskId` 或等价失败信息
- **THEN** 共享契约必须显式导出这些字段
- **AND** 生成 client、测试夹具和验收链不得继续使用过期字段形状冒充当前契约
