# 变更提案：Chat Hardening Step 01 CUID 契约与 ID 校验修复

## 为什么要做

当前 `apps/api` 的 chat 主数据使用 Prisma `cuid()` 作为会话、消息和任务标识，但控制器 DTO 里仍有多处按 UUID 校验参数。这会让真实的 `cuid` 请求在进入业务逻辑前就被错误拒绝。

如果不先修这一步：

- 已落地的 chat 接口无法稳定消费当前数据库真相源
- 后续的 runtime 关联、轮询完成语义和失败重试都会建立在错误的输入契约上
- OpenAPI 与服务端真实可接受输入会持续漂移

## 本次变更包含什么

- 统一 chat 相关接口的 ID 输入契约，使其与 Prisma `cuid` 真相源一致
- 清理会话、任务和消息接口中把平台主键误写成 UUID 的校验与文档
- 为当前 ID 契约补齐测试与 OpenAPI 描述

## 本次变更不包含什么

- runtime task 与平台 task 的关联修复
- assistant 消息的最终落地语义修复
- dispatch 失败与重试闭环修复

## 预期结果

1. 客户端携带合法 `cuid` 访问 chat 读取、事件和重试接口时，不会在参数校验层被误拒。
2. OpenAPI 与 DTO 文档能反映当前平台主键的真实格式。
3. 后续 chat hardening step 都可以基于一致的 ID 契约继续推进。

## 影响范围

- `apps/api/src/modules/chat/dto/*`
- `apps/api/src/modules/chat/chat.controller.ts`
- `apps/api/src/modules/chat/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`

