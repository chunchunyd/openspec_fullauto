# 变更提案：Chat Hardening Step 13 Task Events 无 Runtime 链接时保留平台终态语义

## 为什么要做

本轮验收确认，`getTaskEvents()` 现在虽然已经能通过 `errorCode` / `errorMessage` 区分“runtime 未关联”这类受控语义，但只要 `runtimeTaskId` 为空，当前实现仍会无条件返回 `status=UNKNOWN`、`isCompleted=false`。这会把已经持久化成 `FAILED` 或其他终态的平台 task 再次压扁成“看起来还没完成”的空页，和 step-04 / step-05 建立的失败主线重新打架。

这一步继续沿用 `chat-hardening` 作为 series prefix，只收口“无 runtime 链接时的 task-events 状态语义”，不再混入 finalize 恢复逻辑。

## 本次变更包含什么

- 调整 `runtimeTaskId` 缺失分支的 task-events 状态投影，让 `status` / `isCompleted` 优先保留平台 task 已知状态，尤其是终态结果
- 保留 `RUNTIME_TASK_NOT_LINKED` 这类受控错误字段，但不再用它覆盖掉平台 task 已持久化的真实状态
- 对齐 service、controller、DTO、Swagger、`packages/api_contracts` 与代表性文档中的无 runtime 链接语义

## 本次变更不包含什么

- finalize 完整目标态补偿与 assistant 已落库的 content-free recovery
- 新的 runtime transport、push 通道或任务状态机扩展
- send / retry 成功响应元数据范围扩张

## 预期结果

1. dispatch 失败或其他无 runtime 链接的终态任务，在 task-events 读取时仍能保留真实的终态语义。
2. `errorCode` / `errorMessage` 继续表达“为什么当前没有 runtime 事件”，但不再把平台已知状态抹平成 `UNKNOWN`。
3. 共享 OpenAPI 与消费方文档可以同时看到“无 runtime 链接”和“平台 task 真实状态”这两层信息。

## Capabilities

### New Capabilities

- 无

### Modified Capabilities

- `chat`: 收紧无 runtime 链接时的 task-events 状态语义，要求对外结果保留平台 task 已知状态和完成态
- `api-contracts`: 更新 task-events 共享 OpenAPI，使受控错误字段与平台 task 状态语义能够同时表达

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- 如 task-events 使用说明已有模块文档，可能影响 `apps/api/README.md`
