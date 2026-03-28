# 变更提案：P0 BullMQ 队列基建

## 为什么要做

当前仓库已经存在 `apps/worker` 应用名与若干 `processor` / `dispatcher` 目录骨架，但实际源码仍是空壳，尚未形成可复用的异步任务基础设施。

与此同时，`repository-structure` 真相源已经明确要求：

- `apps/api` 与 `apps/worker` 之间的跨进程异步工作必须通过显式队列或任务契约完成
- `libs/queue` 应负责队列运行时基础设施
- `packages/job_contracts` 应负责共享任务契约
- `apps/worker` 应负责 processor、scheduler 与具体执行逻辑

如果不先建立一套统一的队列基建，后续 `auth`、通知、审核、AI Agent 任务、摘要与分析聚合都很容易出现以下问题：

- `api` 直接同步执行本应异步化的慢任务
- `api` 与 `worker` 各自散落字符串形式的 queue name、job name 和 payload
- 业务模块各自直接使用底层 BullMQ / Redis API，缺少共享封装
- 重试、失败观测、日志与最小验收方式不统一
- scheduler、producer、processor 的职责边界混乱

因此需要先通过一个独立的小 change，建立首期 BullMQ 队列基建。

## 本次变更包含什么

本次变更聚焦于 NestJS + BullMQ 的首期队列基础设施，范围包括：

- 明确首期队列方案采用 `@nestjs/bullmq` + BullMQ + Redis
- 定义 `libs/queue` 的职责边界，明确它负责连接配置、NestJS 接线、队列注册辅助和共享发布能力
- 定义 `packages/job_contracts` 的职责边界，明确它负责 queue name、job name 和共享 payload 契约
- 定义 `apps/worker` 的职责边界，明确它负责 processor、scheduler 和具体执行逻辑
- 约定首期 job 的重试、退避、失败观测和基础日志要求
- 约定 scheduler 与 queue 的关系，明确定时器负责“何时投递”，processor 负责“如何执行”
- 为后续业务 change 提供最小 smoke path，例如 `system` 或等价基础调试任务
- 要求同步补齐 `libs/queue` README、必要注释以及相关入口文档

## 本次变更不包含什么

本次变更不包含以下内容：

- 具体业务能力的完整异步化改造
- 大规模任务编排、任务依赖图或工作流引擎
- 多队列优先级调度策略的完整建设
- 分布式 saga、任务补偿或高级幂等治理体系
- 所有 `auth`、通知、审核或 Agent 任务的一次性实现

## 预期结果

完成后，项目应具备以下结果：

1. 仓库中存在一套可复用的 `libs/queue` BullMQ 运行时基础层
2. `api` 与 `worker` 之间的异步任务契约有统一落位，不再靠散落字符串拼接
3. `worker` 拥有最小可运行的 processor 接线和 smoke job 验证路径
4. 后续业务 change 可以在共享队列基建之上逐步补具体 job，而不必重新争论选型和边界
5. 队列相关 README、注释和入口文档要求被一起固化

## 影响范围

本次变更主要影响：

- 新增的 `queue` capability
- `repository-structure` 中与 `libs/queue`、`packages/job_contracts`、`apps/worker` 相关的约束细化
- `apps/api`、`apps/worker` 与 Redis 之间的异步任务接线方式
- 后续所有依赖后台任务的业务 change
