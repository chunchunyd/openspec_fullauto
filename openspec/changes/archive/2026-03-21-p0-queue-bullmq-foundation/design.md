# 设计说明：P0 BullMQ 队列基建

## 目标

本次设计的目标不是提前实现所有业务 job，而是先建立一条稳定、可复用的异步任务基础链路：

1. `api` 能明确地投递 job
2. `worker` 能明确地消费 job
3. queue name、job name 与 payload contract 有单一落位
4. 重试、失败观测、最小日志与 smoke 验证路径有统一规则

## 为什么选 BullMQ

首期建议采用 `@nestjs/bullmq` + BullMQ，原因如下：

- NestJS 官方提供 BullMQ 集成，适合在 Nest 模块体系中接入 producer 和 processor
- BullMQ 底层使用 Redis，和当前项目已建立的 Redis 基建一致
- 它天然适合 `api` 生产 job、`worker` 异步消费的分进程模型
- 重试、延迟、并发、失败事件和队列事件能力足以覆盖当前首期需求

本次不建议继续停留在自定义“dispatcher + processor 空壳”命名层，也不建议首期自己实现一套 Redis 列表轮询队列。

## NestJS 中的队列到底是什么

在这个项目里，可以把 NestJS 队列先理解成 4 个角色：

```txt
HTTP / service flow
        |
        v
 producer (apps/api)
        |
        v
 BullMQ queue in Redis
        |
        v
 processor (apps/worker)
        |
        v
 business execution
```

更具体一点：

- `BullModule.forRoot(...)`
  - 配置队列系统如何连接 Redis
- `BullModule.registerQueue(...)`
  - 声明一个具名队列，例如 `system`、`moderation`、`agent-task`
- producer
  - 在 `api` 或其他运行时里把 job 投进去
- processor
  - 在 `worker` 里消费某个具名队列中的 job

要注意区分两件事：

- queue 解决的是“异步执行”
- scheduler 解决的是“什么时候触发投递”

也就是说，cron 或定时器不应直接承载完整业务处理逻辑；它更适合在到点时向队列投递一个 job，再由 worker 真正执行。

## 分层模型

### 1. 共享队列运行时层：`libs/queue`

职责：

- BullMQ / NestJS 队列接线
- 连接配置读取与生命周期管理
- 统一 `QueueModule`
- 共享的 queue 注册辅助
- 共享的 producer 辅助封装
- 默认重试、退避和失败观测接线

不负责：

- 具体业务 job 的执行逻辑
- 单一业务模块自己的 payload 业务语义
- 跨运行时共享 contract 之外的字符串散落管理

### 2. 共享任务契约层：`packages/job_contracts`

职责：

- queue name 常量
- job name 常量
- 共享 payload 类型或 schema
- 版本化 contract 的公开入口

这层的意义是让 `api` 和 `worker` 依赖同一套任务命名和 payload 结构，而不是各自手写：

- `'agent-task'`
- `'moderation'`
- `'send-sms'`

这些字符串如果散落在应用目录里，后续会很快漂移。

### 3. Worker 执行层：`apps/worker`

职责：

- queue processor
- queue event listener
- scheduler
- 具体业务 job 执行逻辑

这里保留真正的“做事”逻辑，不把它上收到 `libs/queue`。

## 首期目录建议

```txt
libs/queue/
├─ package.json
├─ README.md
└─ src/
   ├─ index.ts
   ├─ queue.module.ts
   ├─ queue.constants.ts
   ├─ queue.types.ts
   ├─ queue-producer.service.ts
   └─ queue-options.factory.ts

packages/job_contracts/
└─ src/
   ├─ index.ts
   ├─ queue-names.ts
   ├─ job-names.ts
   └─ system/
      └─ system-job.contract.ts

apps/worker/src/
├─ worker.module.ts
├─ jobs/
│  └─ system.processor.ts
└─ schedulers/
   └─ ...
```

## Redis 与队列的关系

`libs/queue` 与 `libs/cache` 可以共享同一个 Redis 基础设施地址，例如同一个 `REDIS_URL`，但不建议把 BullMQ 直接耦合到 `RedisService` 上。

原因：

- BullMQ 对 worker、events 和阻塞消费有自己的连接语义
- queue runtime 的职责和通用缓存原语不同
- 强行共用同一层抽象，容易让 `cache` 与 `queue` 边界混乱

因此更推荐：

- 环境变量层共享同一 Redis 端点
- `libs/cache` 维护缓存原语
- `libs/queue` 维护 BullMQ 运行时封装

## 首期最小 smoke path

为了验证基建通路，首期建议包含一个最小 smoke job，而不是直接绑定真实业务。

例如：

- queue: `system`
- job: `system.ping`

其作用不是承载长期业务需求，而是验证：

- `api` 可以投递
- `worker` 可以消费
- 基础日志、重试和失败观测已经接通

这样做可以降低首个业务 job 就把多种复杂语义混进基建层的风险。

## 命名与 contract 规则

首期建议从第一天就统一以下约定：

- queue name 代表处理通道或工作域，例如 `system`、`moderation`、`agent-task`
- job name 代表该通道下的具体动作，例如 `system.ping`
- queue name 与 job name 必须集中定义在 `packages/job_contracts`
- producer 与 processor 不应在应用代码中长期直接写散落字符串

如果未来 payload 需要 runtime validation，可以继续在 `packages/job_contracts` 中升级为 schema 化 contract；首期至少先保证单一命名源与类型入口。

## 重试、失败与日志

首期建议 `libs/queue` 默认提供以下基础策略：

- job 允许配置 `attempts`
- 支持基础 `backoff`
- 对 job 开始、成功、失败记录结构化日志
- worker 至少能观测失败事件与基础上下文

本次设计刻意不把完整 dead-letter queue 体系做重，但必须保留后续扩展空间。

首期可以接受：

- 先以 BullMQ 自带失败状态与失败事件作为观测基础
- 在后续更具体的业务 change 中，再根据真实需求提炼独立死信处理策略

## 与后续 change 的关系

该 change 完成后，后续 change 应默认建立在这套异步基建之上，例如：

- `auth` 中短信发送异步化
- 内容审核回调
- Agent 任务执行
- 聚合、摘要、通知等后台任务

它们只需要补自己的 job contract 和 processor，不再重新选择队列方案或复制基础接线。
