# 变更提案：Analytics Part1 Step 07 Duplicate Conflict 受控失败语义收口

## 为什么要做

本轮验收发现 analytics 当前对 duplicate event 的处理还是“先查再写”，一旦遇到并发重复写入，数据库唯一约束抛出的冲突会被包成存储失败，而不是受控的 duplicate 结果。这样会让正常重放或并发重复事件污染基础设施错误统计，也不符合 step-02 对“去重或等价保护 + 受控失败语义”的承诺。

这一步继续沿用 `analytics-part1` 作为 series prefix，只收口 duplicate conflict 的分类与 safe emitter 返回语义，不在这一轮同时扩 migration、来源语义或更复杂的重试队列。

## 本次变更包含什么

- 识别 analytics 原始事件写入中的唯一约束冲突，并把它归类为 duplicate 而不是真实存储故障
- 收口 `emitServerEventSafe` 等非阻塞路径对 duplicate conflict 的结构化返回
- 为 duplicate fast-path、唯一约束兜底路径和真实存储失败路径补齐分类测试

## 本次变更不包含什么

- tracking 字典与 emitter 事件名 / 字段口径对齐
- raw event schema migration 与 generated client 收口
- 原始事件 `source` 的客户端 / 服务端区分语义
- 新的后台重试队列、异步补偿任务或幂等表

## 预期结果

1. duplicate event 在预检查或数据库唯一约束兜底路径上都能返回一致的 duplicate 语义。
2. 非阻塞 emitter 不会把 duplicate conflict 误报成存储基础设施故障。
3. analytics 写入失败告警能够更准确地区分“真实存储异常”和“正常 duplicate 冲突”。

## 影响范围

- `apps/api/src/modules/analytics/analytics.service.ts`
- `apps/api/src/modules/analytics/analytics.repository.ts`
- `apps/api/src/modules/analytics/__tests__/*`
- 如需补充错误码说明，可能影响 analytics 模块注释或相关说明文档
