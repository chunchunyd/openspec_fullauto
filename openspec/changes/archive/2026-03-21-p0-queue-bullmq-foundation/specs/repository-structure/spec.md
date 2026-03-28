# Delta for Repository Structure

## ADDED Requirements

### Requirement: 仓库必须为 BullMQ 队列基建提供稳定分层

系统必须将 BullMQ 队列运行时、共享任务契约和 worker 执行逻辑分层管理，而不是把连接、契约和执行器混在同一应用目录中。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `libs/queue` 负责 BullMQ / NestJS 队列接线、共享 producer、连接配置和基础失败观测
- `packages/job_contracts` 负责 queue name、job name 与共享 payload contract
- `apps/worker` 负责 processor、queue event listener、scheduler 和具体 job 执行逻辑


#### Scenario: API 投递后台任务

- WHEN `apps/api` 需要投递后台任务
- THEN 它必须通过 `libs/queue` 发送消息
- AND 投递使用的 queue name、job name 和 payload contract 必须来自 `packages/job_contracts`

#### Scenario: Worker 消费后台任务

- WHEN `apps/worker` 消费后台任务
- THEN 它必须在自身运行时内保留 processor 和具体 job 执行逻辑
- AND 不应把 job 执行逻辑回写到 `libs/queue` 或 `packages/job_contracts`

### Requirement: 仓库必须区分队列执行与定时触发

系统必须区分“何时投递任务”和“如何执行任务”两类职责，避免把 scheduler 误建成完整业务执行器。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 定时触发后台任务

- WHEN 系统需要按时间触发某个后台任务
- THEN scheduler 应负责在适当时间向具名队列投递 job
- AND 具体业务处理应由 worker 中的 queue processor 执行

#### Scenario: 手动或同步流程触发后台任务

- WHEN API 同步流程需要把慢操作改为异步执行
- THEN API 应在请求链路中负责投递 job
- AND 不应直接跨进程调用 worker 内部执行逻辑
