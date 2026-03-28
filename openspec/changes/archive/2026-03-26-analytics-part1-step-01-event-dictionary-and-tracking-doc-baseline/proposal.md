# 变更提案：Analytics Part1 Step 01 事件字典与 Tracking 文档基线

## 为什么要做

当前 `analytics` 能力尚未落地，而 `docs/tracking/` 目录也还没有正式的事件字典真相源。作为 `analytics-part1` 的起点，本 step 先只做 tracking 基础层，把事件命名、属性口径、上下文要求和版本维护方式写清楚，避免后续采集与埋点在不同模块里各自发散。

本批 change 使用 `analytics-part1` 作为 series prefix，且 `part1` 只覆盖 tracking 基础层。当前 step 先以 `docs/tracking/` 与 `analytics` spec 为真相源，不新增新的共享 schema 包、runtime 契约或聚合流水线前置 change。

## 本次变更包含什么

- 在 `docs/tracking/` 建立首期事件字典与 tracking 文档真相源
- 定义事件名称、事件含义、关键属性、最小上下文和版本维护方式
- 划定客户端事件、服务端事件与审计记录的 owner 边界

## 本次变更不包含什么

- 原始事件接收与持久化实现
- 指标聚合、看板报表或 BI 分析能力
- 客户端 SDK、大规模事件接线或全模块覆盖

## 预期结果

1. 首期 analytics 有统一可引用的事件字典来源。
2. 后续原始事件接收和服务端发射可以直接复用统一口径。
3. 埋点、审计与业务真相源之间的 owner 边界更清晰。

## 影响范围

- `docs/tracking/*`
- `openspec/specs/analytics/spec.md`
