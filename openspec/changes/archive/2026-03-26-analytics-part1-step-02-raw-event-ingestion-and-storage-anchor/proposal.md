# 变更提案：Analytics Part1 Step 02 原始事件接收与存储锚点

## 为什么要做

只有事件字典还不足以支撑真正的 analytics 接入。作为 `analytics-part1` 的第二步，需要先建立低耦合的原始事件接收与 append-only 存储锚点，为后续服务端发射、客户端埋点和指标派生提供统一落点，而不是让各模块直接写各自的临时表或日志。

本批 change 继续沿用 `analytics-part1` 作为 series prefix，且 `part1` 仍只覆盖 tracking 基础层。当前 step 限定在 API 内的原始事件入口与存储锚点，复用 step-01 的事件字典，不额外引入新的 runtime 契约、共享 schema 包或聚合流水线前置 change。

## 本次变更包含什么

- 建立原始事件接收入口或等价 collector 边界
- 定义最小上下文、基础校验和 append-only 存储锚点
- 为后续服务端发射器和客户端埋点保留统一写入入口

## 本次变更不包含什么

- 指标聚合、看板查询或 ETL 流水线
- 客户端 SDK 批量接入
- 复杂实时流处理或完整归因体系

## 预期结果

1. analytics 拥有统一的原始事件落点。
2. 事件写入在进入存储前具备最小上下文与基础校验。
3. 后续 step 可以在不改写存储边界的前提下补 emitter 和指标派生。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/analytics/*`
- `packages/api_contracts/openapi/openapi.json`
