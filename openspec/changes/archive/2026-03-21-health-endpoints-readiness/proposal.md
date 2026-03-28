# 变更提案：服务健康检查路径与 Readiness 修正

## 为什么要做

当前仓库已经开始接入共享可观测性层，并且 README 已经对外宣称了统一的 health / live / ready 端点。

但当前实现存在两个会直接影响开发联调和后续运行时部署的问题：

- API 与 worker 的 health controller 路径存在重复前缀，实际暴露路径与 README 不一致
- readiness 当前只是复用共享基础 `HealthService` 的默认实现，没有明确接入应用实际依赖检查，容易出现“依赖已断但仍返回 ready”的假阳性

此外，worker 当前还保留了一条独立的静态 `/health` 返回，导致同一运行时同时存在两套不同语义的健康检查实现。

这类问题虽然看起来不大，但会直接影响：

- 本地开发和 smoke test
- Docker / 容器编排健康探针
- queue、auth、sms 等后续 change 的联调体验
- 未来 adapter / 平台内核演进时的运行时可观测性基础

因此需要先用一个小 change，把 health 路径和 readiness 语义修正到可用状态。

## 本次变更包含什么

本次变更聚焦于 API 与 worker 的健康检查行为修正，范围包括：

- 明确 `GET /health`、`GET /health/live`、`GET /health/ready` 为 API 和 worker 的规范端点
- 修正当前 controller 路由拼接错误，保证实际路径与文档一致
- 清理 worker 中重复或冲突的 health 暴露方式
- 为 API 与 worker 分别建立应用级 readiness 检查，至少覆盖各自实际依赖的最小健康状态
- 同步补齐测试计划、README 和必要注释

## 本次变更不包含什么

本次变更不包含以下内容：

- 完整 observability 基建的所有能力
- metrics、tracing、APM 或告警接入
- 非 health 相关的日志字段重构
- queue、sms、auth 等业务能力的额外功能实现

## 预期结果

完成后，项目应具备以下结果：

1. API 与 worker 都稳定暴露统一的 `/health`、`/health/live`、`/health/ready` 端点
2. README 中的健康检查说明与真实运行时行为一致
3. readiness 不再只是“进程活着”，而是能反映最小关键依赖是否可用
4. worker 不再保留重复且语义冲突的 health 暴露方式

## 影响范围

本次变更主要影响：

- `apps/api` 的 health controller 与 readiness 接线
- `apps/worker` 的 health controller 与 readiness 接线
- 共享 `observability` 层中 health service 的使用方式
- 根 README 中健康检查说明
