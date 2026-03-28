# Delta for API Contracts

## ADDED Requirements

### Requirement: 共享 OpenAPI 产物必须反映已交付的 admin-audit-part1 接口语义

系统必须让共享 OpenAPI 产物反映已交付的 `admin-audit-part1` 接口语义，包括后台用户读取、用户治理动作和审计中心查询的当前状态码、代表性成功结构与受控失败结构。 The system MUST ensure the shared OpenAPI artifact reflects the delivered admin-audit-part1 interface semantics.

#### Scenario: 导出后台用户治理接口契约

- WHEN 后台用户治理接口的运行时状态码、响应结构或错误语义发生实质对齐
- THEN 重新导出的共享 OpenAPI 产物必须体现该对齐后的结果
- AND 不得继续保留与运行时不一致的旧状态码或旧响应结构

#### Scenario: 消费方读取 admin-audit-part1 共享契约

- WHEN 管理端或其他消费方读取 `admin-audit-part1` 对应的共享 OpenAPI 产物
- THEN 它们必须能够看到当前已交付接口的正式契约语义
- AND 不应继续依赖过期的注解结果或本地口头约定推进接入

