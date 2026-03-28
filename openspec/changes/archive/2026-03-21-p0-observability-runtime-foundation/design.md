# 设计说明：P0 服务端可观测性基建

## 目标

本次设计的目标不是一次性把所有 observability 能力做满，而是先建立服务端最小但稳定的共享基线，让后续 change 能在统一规则上继续补细节。

重点解决四件事：

1. `libs/observability` 到底负责什么
2. `api` 请求日志和 `worker` 任务日志如何对齐
3. health / readiness 应该怎样共享而不侵入业务
4. mobile 与服务端的日志边界如何保持清晰

## 分层原则

### 1. 服务端共享运行时层：`libs/observability`

职责：

- 统一日志服务或 logger adapter
- 结构化日志字段约定
- 请求 / 任务上下文提取与注入辅助
- health / readiness 支撑能力
- 与 NestJS 运行时的共享接线

不负责：

- 具体业务模块的全部埋点策略
- 前端 / mobile 客户端日志实现
- 数据分析、行为埋点和 BI

### 2. 应用运行时层：`apps/api` 与 `apps/worker`

职责：

- 在合适的入口接入共享 observability module
- 将请求、job、scheduler 等上下文传入共享日志层
- 保留本应用特有的 controller / bootstrap / health 组合方式

### 3. 业务模块层

职责：

- 在关键状态流转、外部依赖调用、失败与降级点补充业务语义日志
- 复用共享字段和共享 logger，而不是再造一套日志基础设施

## 首期能力范围

首期建议只做对后续 change 最有杠杆的部分：

- 统一 `LoggerService`
- API 请求上下文日志
- worker / queue job 上下文日志
- 基础错误日志约定
- 统一 health / readiness 支撑能力

本次刻意不纳入：

- 完整分布式 tracing
- metrics SDK 与 dashboard
- 第三方 APM 深度集成
- 告警系统

## 为什么 observability 应该排在 auth 之前

当前后续高概率要推进的 change 至少包括：

- `sms` 共享层
- `auth` 重做
- queue / worker 完整接线

这些 change 都会涉及：

- 外部依赖调用
- 重试 / 失败 / 限流
- 安全边界
- request 与 job 的跨链路问题定位

如果没有统一 observability，后面会一边做业务一边争论日志字段和错误输出方式，成本会很高。

## API 与 worker 的上下文字段

建议从第一天统一一套最小字段集合。

### 请求链路建议字段

- `requestId`
- `correlationId`
- `userId`（如可得）
- `route`
- `method`
- `statusCode`
- `durationMs`
- `clientIp`
- `deviceId`（如可得且符合隐私约束）

### worker / queue 链路建议字段

- `jobId`
- `jobName`
- `queueName`
- `attempt`
- `correlationId`
- `userId`（如 payload 可安全提取）
- `durationMs`
- `result`

要求：

- 字段命名在 `api` 与 `worker` 间尽量一致
- 用户敏感信息不得直接明文写入日志
- 若上游已带 `correlationId`，应沿链路透传到 queue job

## health / readiness 的边界

health 能力应拆成两层：

- `libs/observability`
  - 提供共享 health helper、基础检查组合或支撑 service
- `apps/api` / `apps/worker`
  - 决定具体暴露哪些 controller 与端点

这样可以保证：

- 共享逻辑集中
- HTTP 入口仍属于应用运行时
- 不破坏 repository-structure 中“共享库不直接拥有应用级 HTTP 入口”的原则

## queue 与 observability 的关系

`p0-queue-bullmq-foundation` 正在开发，因此本 change 不应与其实现层强耦合，但应提前固定后续接线原则：

- job 开始、成功、失败与重试应使用共享日志字段
- queue / processor / scheduler 的日志应统一落在 `libs/observability` 提供的 logger 能力上
- queue change 中如果暂时使用最小日志输出，后续应能平滑切入本 change 定义的共享日志层

也就是说，本次设计是 queue、sms、auth 的共用后置基线，而不是重新发明 queue 逻辑。

## mobile 边界

mobile 需要自己的日志基础设施，但本次 change 只做两件事：

- 明确 mobile 不直接复用服务端 NestJS observability runtime
- 建议未来 mobile 与服务端尽量对齐字段名、环境名、脱敏约定和 correlation id 语义

这意味着：

- 服务端共享实现放在 `libs/observability`
- mobile 未来可单独起 `mobile-logging-foundation` 之类的 change

## 首期目录建议

```txt
libs/observability/
├─ README.md
└─ src/
   ├─ index.ts
   ├─ observability.module.ts
   ├─ logger.service.ts
   ├─ logging.interceptor.ts
   ├─ request-context.service.ts
   ├─ health/
   │  ├─ health.controller.ts
   │  └─ health.service.ts
   └─ types/
      └─ log-context.types.ts
```

如果当前仓库暂时还不准备拆太多文件，也至少应保证：

- logger
- context
- health

这三个概念不要继续混成单文件占位壳。

## 日志与注释要求

本次 change 本身应同步补齐：

- `libs/observability/README.md`
  - 说明职责边界、公开入口、字段约定、脱敏约定和使用方式
- 根 README 或相关入口文档
  - 如 health 端点、开发命令或环境变量说明发生变化，应同步更新
- 必要注释
  - 对 correlation id 透传、脱敏边界、job 日志字段和 health 边界补充说明

## 与后续 change 的关系

该 change 完成后，后续 change 应默认建立在这套 observability 基线上，例如：

- `sms` provider 调用日志
- `auth` 验证码发送、校验失败与会话操作日志
- queue / worker 的 job 处理日志

后续 change 不再各自重新约定“日志怎么打、health 怎么暴露、字段叫什么”。
