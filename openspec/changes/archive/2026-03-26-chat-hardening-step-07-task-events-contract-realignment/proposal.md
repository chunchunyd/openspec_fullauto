# 变更提案：Chat Hardening Step 07 Task Events 契约回对齐

## 为什么要做

经过 `chat-hardening` 前几步之后，`GET /chat/tasks/:taskId/events` 的真实返回已经逐步稳定为以 `content.*`、`progress` 和更完整的状态枚举表达事件语义，但当前 DTO 与 OpenAPI 仍然停留在旧的 `reply.*` 结构和较窄的状态集合上。验收说明这会让前端类型生成、文档理解和后续联调都建立在错误契约上。

本批 change 继续沿用 `chat-hardening` 作为 series prefix，且这一 step 只收口 task events 的接口契约、DTO 和导出文档对齐。当前 step 以 step-02 到 step-06 形成的真实事件语义为准，不再次发明新的事件模型或改变 runtime 事件来源。

## 本次变更包含什么

- 对齐 `GET /chat/tasks/:taskId/events` 的 DTO、控制器文档和 OpenAPI 导出，使其匹配真实返回结构
- 收口 `content.delta`、`content.completed`、`progress`、`PROCESSING`、`UNKNOWN` 等已存在语义的正式契约表达
- 为 task events 契约导出与代表性响应补齐回归校验，避免文档再次漂移

## 本次变更不包含什么

- 再次重构 polling finalize 行为或 dispatch 失败主线
- 引入新的 task event 类型、push 通道或订阅协议
- 前端页面实现或 SDK 封装

## 预期结果

1. task events 的真实响应、DTO 和 OpenAPI 文档保持一致。
2. 前端或其他调用方可以基于导出的契约稳定生成类型和解析逻辑。
3. 后续 chat 验收不再需要依赖源码反推真实字段名和状态枚举。

## 影响范围

- `apps/api/src/modules/chat/*`
- `packages/api_contracts/openapi/openapi.json`

