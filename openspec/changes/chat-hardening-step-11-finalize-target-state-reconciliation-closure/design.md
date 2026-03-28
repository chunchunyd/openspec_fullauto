## Context

`chat-hardening` 在 step-08 已经把 finalize 从“只看 assistant 消息是否存在”收紧到了“assistant + user message”这一层，但本轮 review 继续确认：当前 `finalizeTask` 和 `tryRecoverFinalization` 的 duplicate / recovery 早退条件，仍然没有把 conversation 最近活跃时间和平台 task 成功态纳入完整目标态判断。

这意味着只要某次 finalize 在 assistant 消息和 user message 状态已经补齐之后、conversation / task 还没落稳之前中断，后续重复 finalize 会误判为“已完全收口”，留下永久半成功状态。

## Goals / Non-Goals

**Goals:**

- 将 finalize 的“完成”定义提升为完整目标态，而不是单一 message 状态
- 让 duplicate finalize 与 polling recovery 共享同一套目标态缺口判断
- 让历史半成功状态可以通过后续 polling 继续补齐 conversation / task 相关读模型

**Non-Goals:**

- 不处理 assistant 已存在但 runtime completion payload 缺失时的恢复拆路，该问题留给后续 step
- 不改动 task-events 的 HTTP 承载方式或 `runtimeTaskId` 缺失时的契约语义
- 不引入新的后台扫描器、定时补偿 job 或跨模块运维流程

## Decisions

### 1. 将 finalize 完成态定义为“四段式目标态”

本 step 会把 finalize 完成态统一定义为以下目标同时成立：

- assistant 消息已存在且保持幂等
- 触发该次回复的 user message 已进入 `COMPLETED`
- conversation 最近活跃时间或等价排序读模型已对齐到最终回复结果
- 平台 task 已进入 `SUCCEEDED` 终态

不再接受“只要 assistant 或 user message 已完成就可以提前返回”的局部判定，因为它会把剩余读模型缺口永久隐藏掉。

### 2. duplicate finalize / polling recovery 必须共用同一套缺口检查

本 step 会把“当前还缺哪一段目标态”的判断收敛为单个受控分支，让 `finalizeTask()` 和 polling recovery 都基于同一份 durable state 快照决定：

- 是否允许 early return
- 是否继续补 user message / conversation / task
- 是否只需要幂等地补剩余状态

不继续维持“finalize 一套判定、recovery 另一套判定”的分叉，因为这会再次制造 source-of-truth drift。

### 3. 优先在本地数据库侧压缩半成功窗口

assistant 消息、user message、conversation 和平台 task 都属于平台数据库拥有的状态。本 step 优先使用事务或等价受控仓储封装，把这些写入压缩到同一条平台侧 reconcile 主线中。

如果实现中受现有 service 边界限制，至少也要保证：

- 早退判断建立在完整目标态上
- 剩余缺口可被后续 polling 幂等补齐

不接受“保留现状，只靠补更多日志观察”的方案，因为问题本身就是恢复判定过窄，不是单纯可观测性不足。

## Risks / Trade-offs

- [完整目标态检查会增加一次或少量额外读取] -> 这些读取只发生在 finalize / recovery 热点，换来更稳定的最终一致性，代价可接受
- [assistant / chat / agent-task 可能跨现有 service 边界] -> 优先把判断和写入收敛到平台自有数据库层，不把 runtime 调用并入事务
- [历史半成功数据已经存在] -> 新的缺口检查应允许后续 polling 主动识别并补齐，而不是要求人工清洗

## Migration Plan

本 step 不涉及 schema 迁移。部署重点是先更新 finalize / recovery 的目标态判断与测试，随后依赖后续 polling 访问逐步收口历史半成功状态。

## Open Questions

- 如果实现时发现会话列表还依赖额外排序投影字段，本 step 应继续沿用“完整目标态”思路把它纳入同一条 reconcile 判断，不再额外新开平行 step。
