## Context

当前 `tryRecoverFinalization()` 已经能识别“assistant 消息已存在但 user message 尚未完成”的部分成功状态，但它在进入补偿前仍会继续查找 runtime `MESSAGE_COMPLETED` 事件和其中的 `content`。这意味着：

- assistant 缺失时，这套逻辑是合理的，因为系统仍需要 completion content 来创建消息
- assistant 已存在时，这套逻辑反而成了多余前置条件，因为补偿剩余读模型并不再需要 runtime content

结果就是：只要 runtime 只保留 `TASK_SUCCEEDED` 之类的终态事件，或 completion payload 本身不可用，assistant 已存在的半成功数据仍然无法继续补偿。

## Goals / Non-Goals

**Goals:**

- 把“创建缺失 assistant”与“补齐已有 assistant 的剩余读模型”拆成两条恢复路径
- 让 assistant 已存在时的 recovery 不再依赖 runtime completion payload
- 保持 assistant 消息缺失时对 completion content 的严格要求，避免凭空生成错误消息

**Non-Goals:**

- 不重新定义 finalize 的完整目标态，该目标态以前一步为基线
- 不改动 `runtimeTaskId` 缺失分支的 task-events 状态承载方式
- 不增加新的后台补偿器或全量历史扫描流程

## Decisions

### 1. 根据 durable state 区分 recovery 模式，而不是继续用单一路径处理所有场景

本 step 会把 recovery 分成两类：

- assistant 消息不存在：必须从 runtime completion payload 恢复最终内容，再创建消息并补齐目标态
- assistant 消息已存在：直接进入 content-free reconcile，只补剩余的 user message / conversation / task 目标态

不再接受“无论是否已有 assistant，都必须先找到 `MESSAGE_COMPLETED` payload”的单一路径，因为它把 durable state 已经具备的信息浪费掉了。

### 2. assistant 已存在时，以平台 durable state 为补偿真相源

当 assistant 已经在平台数据库中存在时，本 step 会把它视为当前补偿的内容真相源；此时恢复逻辑只负责：

- 判断还有哪些目标态缺口
- 幂等补 user message / conversation / task

不会在这一分支重新要求 runtime 再次提供 completion content，也不会尝试覆写已经落库的 assistant 内容。

### 3. 继续保留“assistant 缺失时必须有 completion content”的约束

assistant 缺失的场景本质上仍是“需要把最终回复重新落库”。这类恢复不能凭借终态事件空推断消息正文，因此仍需要 runtime completion payload 或等价正式来源。

不把这两类恢复混在一起，是为了同时保证：

- 已有 assistant 的补偿尽可能稳
- 缺失 assistant 时仍不牺牲内容正确性

## Risks / Trade-offs

- [assistant 已落库但内容本身是坏数据] -> 本 step 只负责剩余读模型补偿，不负责修复既有 assistant 正文；避免 scope 膨胀
- [recovery 路径分支更多] -> 用明确的 durable-state 判断和结构化日志收敛复杂度
- [runtime 终态事件与 durable assistant 内容不一致] -> 以平台已落库 assistant 为准，避免恢复路径再次修改历史消息正文

## Migration Plan

本 step 不涉及 schema 迁移。部署后，已有“assistant 已存在但 runtime 不再提供 completion payload”的半成功任务，可以在后续 polling 中逐步完成补偿。

## Open Questions

- 若实现时发现 conversation 读模型补偿需要读取 assistant 消息本身的创建时间或其他持久化字段，应继续沿用“assistant 已落库即以 durable state 为准”的原则，不额外回退到 runtime payload。
