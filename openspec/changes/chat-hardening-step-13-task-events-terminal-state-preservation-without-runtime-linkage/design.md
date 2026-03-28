## Context

当前 `chat` 在 `runtimeTaskId` 缺失时，已经会返回 `RUNTIME_TASK_NOT_LINKED` 这一层受控错误语义；但同一分支仍把 `status` 固定压成 `UNKNOWN`、`isCompleted` 固定压成 `false`。这与平台 task 自己已经持久化的状态可能冲突，尤其是：

- dispatch bootstrap 已失败，平台 task 已是 `FAILED`
- 未来如果出现其他无 runtime 链接的终态任务，平台 task 也可能已经是 `CANCELLED` 或等价终态

step-09 的目标本来是让 task-events 契约既表达受控错误，又保留真实状态语义；当前实现只收口了前半部分。

## Goals / Non-Goals

**Goals:**

- 让 `runtimeTaskId` 缺失时的 task-events 结果继续保留平台 task 已知状态与完成态
- 保留 `RUNTIME_TASK_NOT_LINKED` 等受控错误字段，表达“为什么当前没有 runtime 事件”
- 让 service、controller、DTO、OpenAPI 和文档对这套语义保持一致

**Non-Goals:**

- 不改动 finalize、assistant 恢复或 send / retry 主线
- 不重新设计 task-events 为 4xx / 5xx 错误响应
- 不扩展新的 runtime transport 或 task 状态机

## Decisions

### 1. `runtimeTaskId` 缺失时，以平台 task 记录作为状态真相源

本 step 会在 `runtimeTaskId` 为空时优先读取平台 task 已持久化状态，并把它映射到 chat task-events 的 `status` / `isCompleted`：

- 终态任务保留终态结果
- 非终态任务保留当前已知平台状态或等价 chat 状态

不再把所有无 runtime 链接场景统一压成 `UNKNOWN`，因为平台 task 本身已经提供了更可靠的状态信息。

### 2. 受控错误字段继续表达“无 runtime 事件来源”，但不覆盖状态语义

`errorCode=RUNTIME_TASK_NOT_LINKED` 仍然保留，用来告诉调用方“当前没有可读的 runtime 事件流”。但它应当和平台 task 状态共存，而不是把 `status` / `isCompleted` 重写成统一空页。

不采用“终态时去掉 `errorCode`”方案，因为调用方仍需要知道为什么拿不到 runtime 事件明细。

### 3. 共享契约必须允许“受控错误字段 + 已知状态”同时存在

本 step 会同步更新 DTO、OpenAPI 导出和使用说明，让消费方明确看到：

- 当前 task 没有关联 runtime
- 但平台 task 已知状态仍然是 `FAILED` / `QUEUED` / 等价正式状态

这样才能避免前端把“无 runtime 链接”误当成“任务尚未失败或尚未完成”。

## Risks / Trade-offs

- [消费方之前可能把 not-linked 直接等同于 `UNKNOWN`] -> 通过共享契约和文档显式说明“error fields 与 status/isCompleted 可同时存在”
- [平台 task 与 runtime 未来可能短暂不一致] -> 无 runtime 链接时本就没有 runtime 真相源，优先使用平台 durable state 更稳定
- [测试矩阵扩大] -> 重点覆盖 FAILED / 非终态 not-linked 两类代表场景，避免回归

## Migration Plan

本 step 不涉及 schema 迁移。部署重点是同步 service、DTO 与 `openapi-export` 产物，让前端与生成 client 能立即读取新的 not-linked 状态语义。

## Open Questions

- 若实现时发现现有 task 状态到 chat 状态的映射需要复用新的 helper，应继续限制在 chat task-events 语义范围内，不扩展成全仓库状态映射重构。
