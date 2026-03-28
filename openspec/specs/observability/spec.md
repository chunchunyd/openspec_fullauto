# Observability Specification

## Purpose

本规格定义“能干”项目当前服务端共享可观测性层的行为真相源。

首期可观测性能力聚焦于：

- 为 `api`、`worker` 和 `agent-runtime-mock` 提供统一的服务端共享可观测性层
- 统一最小日志上下文字段
- 应用基础脱敏规则
- 为应用级 health / readiness 提供共享支撑能力

## Requirements

### Requirement: 系统必须提供统一的服务端共享可观测性层

系统必须提供统一的服务端共享可观测性层，供 `api`、`worker` 和 `agent-runtime-mock` 等服务端运行时复用，而不是由各运行时分别长期维护漂移的日志基础设施。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期该共享层至少应包括：

- 统一日志接入方式
- 统一上下文字段约定
- 基础错误日志能力
- health / readiness 支撑能力


#### Scenario: API 记录请求链路日志

- WHEN `apps/api` 处理请求链路中的关键开始、成功、失败或降级事件
- THEN 它必须能够通过统一的服务端共享可观测性层记录结构化日志
- AND 不应长期依赖各 controller 或 service 自行拼装互不一致的日志格式

#### Scenario: Worker 记录后台任务日志

- WHEN `apps/worker` 执行 queue job、scheduler 触发任务或其他后台处理
- THEN 它必须能够通过统一的服务端共享可观测性层记录结构化日志
- AND 日志必须能表达任务链路所需的最小上下文

### Requirement: 系统必须统一服务端日志上下文字段

系统必须统一服务端日志的最小上下文字段，以支持请求链路和异步链路的排查与关联。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期上下文字段至少应覆盖：

- request id 或等价请求标识
- correlation id 或等价跨链路标识
- 用户标识（在可安全获取时）
- queue / job 标识（在异步场景中）
- 结果或状态字段


#### Scenario: 请求链路透传上下文

- WHEN API 请求进入系统并触发后续处理
- THEN 系统必须能够在相关日志中保留或生成可追踪的上下文字段
- AND 后续链路不得无故丢失用于排查问题的核心标识

#### Scenario: 异步任务延续上下文

- WHEN 请求链路触发后台 job 并进入 `worker`
- THEN 系统必须能够让异步日志延续关键上下文字段
- AND 队列日志不应完全失去与上游请求的关联能力

### Requirement: 系统必须对服务端日志应用基础脱敏规则

系统必须对服务端日志应用基础脱敏规则，避免把手机号、验证码、token 或其他敏感信息直接作为普通日志正文输出。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 记录认证或短信相关日志

- WHEN 系统记录与认证、短信或会话相关的日志
- THEN 敏感信息必须遵循脱敏或最小输出原则
- AND 日志不得直接暴露验证码、完整手机号或完整 token

### Requirement: 系统必须支持应用级 health 与 readiness 暴露

系统必须支持 `api` 与 `worker` 暴露应用级 health 或 readiness 能力，以支撑本地开发、集成验证和运行时检查。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: API 暴露 health

- WHEN `apps/api` 需要对外暴露运行状态检查
- THEN 它必须能够复用共享可观测性层提供的 health 支撑能力
- AND 具体 HTTP 入口应保留在 API 应用运行时内

#### Scenario: Worker 暴露 health

- WHEN `apps/worker` 需要对外暴露运行状态检查
- THEN 它必须能够复用共享可观测性层提供的 health 支撑能力
- AND 具体 HTTP 入口应保留在 worker 应用运行时内
