# 变更提案：Chat Hardening Step 10 Chat 类型校验与验收链收口

## 为什么要做

本轮验收在 rerun `chat-hardening` 相关 Jest 与 `apps/api` TypeScript 检查时，确认当前系列虽然已经修正了大部分运行时行为问题，但验收链本身还留着两类 drift：一是部分 chat 成功响应 DTO 通过属性默认值导出时会把 `success` 之类的标量字段退化成 `type: object`；二是 chat 相关测试桩还没有完全跟上 `AgentTaskInfo` / `TaskInfoDto` 的最新字段形状，导致 branch-local 类型错误被埋在仓库基线噪音里。

这一步继续沿用 `chat-hardening` 作为 series prefix，只收口 chat 关键响应元数据的导出与验收链，不再扩展新的运行时语义。

## 本次变更包含什么

- 收紧 send / retry / task-events 成功响应的 DTO 与 OpenAPI 导出源，确保布尔标量和 task metadata 字段保持稳定表达
- 更新 chat 相关测试桩、fixture builder 或等价辅助方法，使其与 `AgentTaskInfo` / `TaskInfoDto` 的当前形状一致
- 重新执行 chat-hardening 相关 Jest / TSC / OpenAPI 验收，并区分本 step 直接引入的问题与仓库基线遗留问题

## 本次变更不包含什么

- 新的 runtime 事件语义、task-events 错误承载方式或 finalize 逻辑调整
- 全仓库范围的 `auth`、`libs/*` 或其他非 chat 领域类型债务清理
- 前端页面接入、SDK 封装或发布流程改造

## 预期结果

1. chat 成功响应中的 `success` 等标量字段在共享 OpenAPI 中保持正确的标量类型。
2. send / retry / task-events 关键响应里的 task metadata 字段在 DTO、导出契约和 acceptance 测试之间重新对齐。
3. 后续再次验收 `chat-hardening` 时，可以更清楚地区分 chat 本地回归和仓库基线债务。

## Capabilities

### New Capabilities

- 无

### Modified Capabilities

- `chat`: 补齐发送、重试与 task-events 成功响应中的稳定任务跟踪元数据表达
- `api-contracts`: 收紧共享 OpenAPI 中 chat 成功响应的标量类型与任务元数据字段表达

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `apps/api/src/modules/agent-tasks/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- 如验收命令或 contract 说明已有入口文档，可能影响 `apps/api/README.md`
