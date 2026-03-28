# Delta for Queue

## ADDED Requirements

### Requirement: 系统必须提供统一的 BullMQ 队列运行时接入层

系统必须提供统一的 BullMQ 队列运行时接入层，供 `api`、`worker` 等运行时复用，而不是由各应用分别散落底层 BullMQ 接线。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期该共享层至少应包括：

- 统一 Redis 连接配置入口
- 可复用的 `QueueModule`
- 共享 producer 接入方式
- 基础重试与失败观测能力


#### Scenario: API 投递后台任务

- WHEN `apps/api` 需要异步投递后台任务
- THEN 它必须通过统一的共享队列运行时接入层完成投递
- AND 不应在业务模块内长期直接复制一套底层 BullMQ 初始化逻辑

#### Scenario: Worker 接入共享队列运行时

- WHEN `apps/worker` 需要消费后台任务
- THEN 它必须通过统一的共享队列运行时接入层完成接线
- AND 不应在 worker 内部长期维护另一套分散的基础接线逻辑

### Requirement: 系统必须集中维护共享任务契约

系统必须集中维护 queue name、job name 和共享 payload contract，避免 `api` 与 `worker` 各自维护漂移的本地副本。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 定义首期 smoke job

- WHEN 系统为队列基建建立首期 smoke job
- THEN 该 job 的 queue name、job name 和 payload contract 必须有统一落位
- AND producer 与 processor 必须共同依赖这份共享契约

#### Scenario: 后续能力新增后台任务

- WHEN 后续业务能力新增后台任务
- THEN 它们必须沿用统一的共享任务契约管理方式
- AND 不应在各应用目录中长期散落硬编码字符串和隐式 payload 结构

### Requirement: 系统必须通过具名 processor 消费后台任务

系统必须通过具名 processor 消费后台任务，并将具体执行逻辑保留在 worker 应用自身，而不是回写到共享运行时层中。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: Worker 消费后台任务

- WHEN `apps/worker` 消费某个具名队列中的任务
- THEN 它必须通过对应 queue 的 processor 执行具体逻辑
- AND 具体 job 执行逻辑必须保留在 worker 运行时中

#### Scenario: 定时任务触发后台处理

- WHEN 系统需要按时间触发后台处理
- THEN scheduler 应负责在适当时间投递 job
- AND 具体业务执行仍应由 queue processor 完成

### Requirement: 系统必须具备首期重试与失败观测能力

系统必须为后台任务提供首期可用的重试与失败观测能力，以支持最小可运行的异步链路验收。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 后台任务短暂失败

- WHEN 后台任务因临时性原因失败
- THEN 队列系统必须支持按照统一策略进行重试
- AND 重试策略不应由每个业务模块各自重复发明

#### Scenario: 后台任务最终失败

- WHEN 后台任务在重试后仍然失败
- THEN worker 运行时必须能够观测并记录失败上下文
- AND 后续死信或补偿策略必须建立在这套明确失败观测之上
