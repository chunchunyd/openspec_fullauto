# 变更提案：Chat Hardening Step 09 Task Events 受控错误契约补齐

## 为什么要做

`chat-hardening` 在 step-02 已经把“runtime task 映射缺失”收敛成受控服务语义，在 step-07 也把 task-events 的事件命名、状态枚举和 OpenAPI 基本对齐了，但本轮验收确认这些差异化错误语义还没有真正穿透到 HTTP 契约。当前 controller 会把 `result.error` 静默吞掉，客户端最终只能看到 `status=UNKNOWN` + 空事件列表，分不清是“当前无新事件”“runtime task 尚未建立映射”还是“runtime 暂时不可读”。

这一步继续沿用 `chat-hardening` 作为 series prefix，只收口 task-events 的受控错误 / 未就绪 HTTP 契约，不再混入 finalize 原子修复或 send / retry 验收链清理。

## 本次变更包含什么

- 为 `GET /chat/tasks/:taskId/events` 补齐对外可见的受控错误 / 未就绪字段或等价契约表达
- 对齐 service、controller、DTO、Swagger 和 `packages/api_contracts` 的 task-events 错误语义
- 为 runtime 映射缺失、runtime 暂时不可读与“当前无新增事件”三类轮询结果补齐回归测试

## 本次变更不包含什么

- finalize 的原子收口与读模型补偿
- send / retry 成功响应元数据和类型校验闭环
- 新的 push 通道、前端 SDK 封装或更多 event type 扩展

## 预期结果

1. task-events 调用方能够在 HTTP 契约层区分“无新增事件”“runtime 未映射”和“runtime 暂时不可读”。
2. `chat.service.ts` 中已有的受控错误语义不再在 controller / OpenAPI 层丢失。
3. `packages/api_contracts/openapi/openapi.json` 能稳定表达这套差异化语义，供前端或生成工具直接消费。

## Capabilities

### New Capabilities

- 无

### Modified Capabilities

- `chat`: 收紧 task-events 的对外受控错误语义，要求 HTTP 响应能够保留 not-linked / unavailable / normal-empty 三类区别
- `api-contracts`: 补齐 task-events 共享 OpenAPI 契约中的受控错误 / 未就绪字段表达

## 影响范围

- `apps/api/src/modules/chat/*`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`
- 如 task-events 说明已有入口文档，可能影响 `apps/api/README.md`
