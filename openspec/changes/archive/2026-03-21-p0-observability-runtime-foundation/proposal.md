# 变更提案：P0 服务端可观测性基建

## 为什么要做

当前仓库已经明确把 `libs/observability` 定义为服务端共享可观测性层，但本地实现仍然停留在占位状态，尚未形成真正可复用的日志、健康检查与上下文接线能力。

与此同时，项目正在推进 Redis、队列和 worker 基建。随着 `p0-queue-bullmq-foundation` 进入开发阶段，后续很快会出现以下需要统一支撑的场景：

- `api` 请求链路需要统一结构化日志
- `worker` 与 queue job 需要统一记录开始、成功、失败和重试上下文
- `auth`、`sms`、`queue` 等共享层需要统一日志字段和错误记录方式
- `api` 与 `worker` 都需要稳定暴露 health / readiness 能力

如果没有一套明确的服务端可观测性基建，后续很容易出现：

- API、worker、共享库各自使用不同风格的日志输出
- queue job 的失败上下文和请求日志无法关联
- health 端点、日志字段、脱敏规则和环境区分方式长期漂移
- mobile 误复用服务端 NestJS 日志实现，造成边界混乱

因此需要在后续业务 change 继续展开之前，先补齐一套首期服务端可观测性基建。

## 本次变更包含什么

本次变更聚焦于服务端共享可观测性层，范围包括：

- 定义 `libs/observability` 的职责边界，明确其负责服务端共享日志、请求/任务上下文与 health 支撑能力
- 建立适用于 `api` 与 `worker` 的统一结构化日志字段约定
- 约定请求链路与后台任务链路的上下文字段，例如 request id、job id、queue name、user id、trace/correlation id
- 约定服务端错误日志、关键状态日志与脱敏规则
- 建立首期 health / readiness 接线方式，供 `api` 与 `worker` 复用
- 明确 mobile 只共享字段约定，不直接复用服务端 NestJS 运行时实现
- 要求同步补齐 `libs/observability` README、必要注释和开发入口文档

## 本次变更不包含什么

本次变更不包含以下内容：

- 具体业务模块的完整日志埋点补齐
- 移动端日志实现本身
- 完整 tracing、APM、metrics 平台或供应商接入
- 数据分析埋点、行为分析与 BI 体系
- 告警平台、报表与日志归档策略

## 预期结果

完成后，项目应具备以下结果：

1. 仓库中存在一套可复用的 `libs/observability` 服务端共享运行时基础层
2. `api` 与 `worker` 的日志字段、上下文与 health 接线方式有统一约定
3. queue、sms、auth 等后续 change 能直接复用统一日志与错误上下文，而不是各自重新约定
4. mobile 与服务端的日志边界被进一步明确，不会误把服务端 NestJS 日志层当作客户端日志实现
5. README、必要注释和入口文档要求被一起固化

## 影响范围

本次变更主要影响：

- 新增的 `observability` capability
- `libs/observability` 的目录职责与公开入口
- `apps/api` 与 `apps/worker` 的日志、health 与上下文接线方式
- 后续所有依赖服务端日志与错误观测的共享层和业务 change
