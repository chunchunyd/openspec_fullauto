# 变更提案：Analytics Part1 Step 03 服务端发射器与非阻塞写入边界

## 为什么要做

当原始事件接收与存储锚点建立之后，服务端仍然需要统一的事件发射边界，才能让已经具备主流程的模块以同一种方式接入 analytics。作为 `analytics-part1` 的第三步，本 step 只补通用 emitter 与少量代表性接线，并确保 analytics 写入失败时不会阻塞核心业务流程。

本批 change 继续沿用 `analytics-part1` 作为 series prefix，且 `part1` 仍只覆盖 tracking 基础层。当前 step 复用 step-02 的原始事件入口，优先沿用现有 API 模块与错误处理能力，不新增新的 runtime 契约、移动端共享层或聚合任务前置 change。

## 本次变更包含什么

- 提供统一的服务端 analytics emitter 或等价 facade
- 为事件发射补齐最小上下文装配、错误记录和非阻塞降级语义
- 在当前已实现的核心服务端流程中接入少量代表性发射点

## 本次变更不包含什么

- 客户端 SDK 或移动端埋点接线
- 指标聚合、看板查询或批处理任务
- `chat`、`content` 等尚未稳定模块的全量事件覆盖

## 预期结果

1. 服务端模块拥有统一可复用的 analytics 事件发射边界。
2. analytics 写入异常不会破坏 `auth`、`agents` 等核心业务主线。
3. 后续新模块可以按相同模式继续接入服务端事件。

## 影响范围

- `apps/api/src/modules/analytics/*`
- `apps/api/src/modules/auth/*`
- `apps/api/src/modules/agents/*`
- `packages/api_contracts/openapi/openapi.json`
