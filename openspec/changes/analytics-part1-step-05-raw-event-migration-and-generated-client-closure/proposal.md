# 变更提案：Analytics Part1 Step 05 Raw Event Migration 与 Generated Client 收口

## 为什么要做

本轮验收确认 `analytics-part1` 已经在 `prisma/schema.prisma` 中引入了 `AnalyticsEventSource` 和 `AnalyticsRawEvent`，但分支里没有对应的 Prisma migration，新增测试也暴露出运行时 / 测试侧读取到的 generated client 与当前 schema 没有形成稳定闭环。这样一来，step-02 的“原始事件存储锚点”仍然停留在源码层，无法作为真正可迁移、可验证的能力继续演进。

这一步继续沿用 `analytics-part1` 作为 series prefix，只收口 raw event 存储模型的 deployability 与 generated client 一致性，不在这一轮同时扩 `source` 语义或 duplicate 并发语义。

## 本次变更包含什么

- 为 `AnalyticsEventSource` / `AnalyticsRawEvent` 补齐正式 Prisma migration
- 收口 `db-generate` 后 runtime、测试与当前 analytics schema 的一致性
- 为 analytics 相关验证补齐“新环境可迁移、可生成、可运行”的最小验收链路

## 本次变更不包含什么

- tracking 字典与 emitter 事件名 / 字段口径对齐
- 原始事件 `source` 的客户端 / 服务端区分语义
- duplicate 写入并发冲突的受控失败语义修复
- 新增 analytics 聚合表、报表查询或后台看板

## 预期结果

1. 一个全新环境可以通过正式 migration 建出 analytics 原始事件存储表和必要索引。
2. runtime 与测试读取到的 Prisma contract 与当前 analytics schema 保持一致。
3. `analytics` 基线不再依赖“手工继承已有 generated artifact”才能通过最小验证。

## 影响范围

- `prisma/schema.prisma`
- `prisma/migrations/*`
- `apps/api/src/modules/analytics/__tests__/*`
- 如需补齐生成说明，可能影响 `prisma/README.md` 或相关验证脚本说明
