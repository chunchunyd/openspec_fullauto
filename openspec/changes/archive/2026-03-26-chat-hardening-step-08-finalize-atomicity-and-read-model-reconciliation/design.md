## Context

当前 `chat` 的 polling finalize 已经具备“task 成功但 assistant 消息缺失时尝试恢复”的能力，但 `finalizeTask` 内部仍是顺序式数据库写入：

1. 用 `assistant:{taskId}` 的幂等键创建 assistant 消息
2. 将触发该回复的用户消息状态改为 `COMPLETED`
3. 更新会话 `lastActiveAt` 与列表读模型

这套顺序在“第 1 步成功、第 2/3 步失败”时会留下半成功状态。随后恢复逻辑又只把“assistant 消息是否存在”当成 finalize 已完成的判据，导致系统不再尝试补齐剩余读模型。

## Goals / Non-Goals

**Goals:**

- 让 finalize 在平台侧形成原子化或等价原子化的读模型收口语义
- 让 polling 恢复逻辑能够识别“assistant 已存在但收口未完成”的部分失败状态
- 保持 repeated polling / repeated finalize 的幂等，不重复生成 assistant 消息

**Non-Goals:**

- 不引入新的后台补偿 worker、定时扫描器或跨模块修复平台
- 不修改 task-events 的 HTTP 错误契约
- 不改变 public chat、streaming provider 或 runtime transport 的边界

## Decisions

### 1. 将 finalize 视为“消息 + 状态 + 会话读模型”的整体收口，而不是单点消息写入

本 step 采用单个 finalize/reconcile 入口来驱动 assistant 消息、用户消息状态和会话最近活跃时间的同步收口。实现上优先使用单次数据库事务或等价仓储封装，让三类写入要么一起完成，要么在失败后由后续恢复路径继续补齐。

不继续沿用当前“先建消息，后改状态，再更新时间”的裸顺序写法，因为它会把幂等判断过早绑定到 assistant 消息这一项，导致后续状态无法恢复。

### 2. 恢复逻辑不再把“assistant 消息存在”视为 finalize 已全部完成

恢复路径会改为检查完整目标态：

- assistant 消息是否存在
- 触发该次回复的用户消息是否已进入 `COMPLETED`
- 会话最近活跃时间和等价读模型是否已对齐到最终回复结果

只要任一项未完成，就继续进入受控 reconcile，而不是提前短路返回。

不采用“仅在第一次 finalize 失败时重试、之后全部交给人工”的方案，因为 polling 主线本来就承担这条最终一致性的公开恢复职责。

### 3. 对部分失败和恢复补偿补充结构化日志

本 step 会显式记录：

- 进入恢复路径的原因
- 识别到的部分收口状态
- 补偿成功或失败的关键上下文

这样后续如果仍有 finalize 裂缝，就不必只靠临时控制台日志逆向排查。

## Risks / Trade-offs

- [数据库事务扩大 finalize 临界区] → 只覆盖本地数据库写入，不把 runtime 调用并入事务；保持事务范围尽量小
- [并发轮询可能同时触发 reconcile] → 继续复用 assistant idempotency key，并让用户消息状态/会话更新时间更新具备重复执行安全性
- [历史半成功数据已存在] → 新的恢复逻辑会在后续 polling 中主动识别并补齐，而不是要求人工清理

## Migration Plan

本 step 不涉及 schema 迁移。部署顺序以应用代码为主即可；上线后历史遗留的部分失败会在后续 polling 访问中逐步自恢复。

## Open Questions

- 当前没有额外阻塞性开放问题；若实现时发现会话摘要还依赖额外投影字段，再在本 step 内补充最小必要范围，不新增独立系列。
