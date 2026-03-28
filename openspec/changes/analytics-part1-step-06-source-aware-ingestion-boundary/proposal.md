# 变更提案：Analytics Part1 Step 06 Source-aware Ingestion Boundary

## 为什么要做

验收确认当前 analytics 的统一 ingestion 边界虽然已经有 `AnalyticsEventSource` 枚举，但 `IngestRawEventInput`、service 和 repository 并没有真正透传 `source`，导致所有事件都会按默认值落成 `SERVER`。这会让 step-02 所承诺的“统一承接客户端埋点和服务端事件发射”只剩下一半能力，也会让后续客户端 collector 一接入就污染来源口径。

这一步继续沿用 `analytics-part1` 作为 series prefix，只补来源语义的保存与校验，不同时扩展新的客户端 SDK、controller 或 duplicate 语义。

## 本次变更包含什么

- 在 raw event ingestion 边界中显式承接 `source`
- 让 `emitServerEvent` / `emitServerEventSafe` 继续由服务端 facade 负责填充 `SERVER` 语义
- 为客户端 / 服务端两类写入路径补齐来源保存验证

## 本次变更不包含什么

- tracking 字典与 emitter 事件名 / 字段口径对齐
- raw event schema migration 与 generated client 收口
- duplicate 写入并发冲突的受控失败语义修复
- 新增 analytics HTTP collector 或移动端 SDK

## 预期结果

1. analytics 原始事件存储能够保留 `CLIENT` / `SERVER` 来源差异。
2. 服务端业务模块继续只通过统一 emitter 接入，不必散落拼装 raw ingestion 的来源枚举。
3. 后续客户端 collector 接入时可以复用现有 ingestion 边界，而不会把客户端事件错误写成服务端事件。

## 影响范围

- `apps/api/src/modules/analytics/dto/raw-event.dto.ts`
- `apps/api/src/modules/analytics/analytics.service.ts`
- `apps/api/src/modules/analytics/analytics.repository.ts`
- `apps/api/src/modules/analytics/__tests__/*`
