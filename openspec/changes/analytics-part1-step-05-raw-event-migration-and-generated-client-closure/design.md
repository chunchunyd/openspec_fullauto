# 设计说明：Analytics Part1 Step 05 Raw Event Migration 与 Generated Client 收口

## 目标

- 让 `AnalyticsRawEvent` 从“schema 中定义了，但无法稳定落库 / 验证”的半完成状态，收口为正式可迁移、可生成、可验证的存储基线。

## 边界

- 只处理 raw event 存储结构与 generated client 一致性，不借机扩展新的 analytics 模型。
- 不引入新的聚合表或消费任务。
- 不改变当前业务侧 emitter 的调用语义。

## 方案

### 1. 用正式 migration 固化当前 schema

- 为 `AnalyticsEventSource` 枚举、`analytics_raw_events` 表和相关索引补齐 versioned migration。
- migration 必须与当前 `schema.prisma` 中已经承诺的字段和索引保持一致，避免“schema 与 migration 各说各话”。

### 2. 收口 generated client 的使用闭环

- 让 `pnpm db-generate` 后的 Prisma Client 能稳定暴露 analytics 相关枚举和模型。
- 如果当前 analytics 单测或模块代码对 generated client 的引用路径存在脆弱假设，需要在这一 change 中一并收口。

### 3. 把 fresh setup 纳入最小验收

- 最低目标不是“本机已有 node_modules 时凑巧可跑”，而是“新环境按官方命令 migrate + generate 后能稳定进入 analytics 最小验证链”。
- 因此这一 change 的验证重点是 migration、generate 和 analytics 定向测试之间的连通性。

## 风险与取舍

- 如果只补 migration 不收口 generated client，一样可能在测试或运行时继续看到旧 contract。
- 如果只在本机手工生成 client 而不把验收链写进 change，后续 worktree / CI 仍会重复踩坑。

## 验证重点

- 正式 migration 能建立 `analytics_raw_events` 及其索引。
- `db-generate` 后 analytics 相关代码和单测能读取到正确的 Prisma contract。
- 定向 analytics 验证不再依赖“沿用旧 worktree 生成物”才能通过。
