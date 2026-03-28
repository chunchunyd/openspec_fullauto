# 设计说明：服务健康检查路径与 Readiness 修正

## 目标

本次设计的目标非常聚焦：

1. 统一 health 端点路径
2. 让 readiness 真正表达“是否可接收流量 / 是否可处理任务”
3. 去掉当前 API / worker 中重复和冲突的 health 暴露方式

## 当前问题

### 1. 路由前缀重复

当前 API 与 worker 的 health controller 使用了：

- `@Controller('health')`
- `@Get('/health/live')`
- `@Get('/health/ready')`
- `@Get('/health')`

这会使真实路径变成：

- `/health/health/live`
- `/health/health/ready`
- `/health/health`

但 README 当前对外声明的是：

- `/health`
- `/health/live`
- `/health/ready`

两者不一致。

### 2. readiness 假阳性

当前共享 `HealthService` 的默认实现更像一个基础 helper，而不是应用级就绪检查：

- 它允许应用层注册或覆盖依赖检查
- 但 API 与 worker 当前没有真正注入自己的依赖检查

因此即便数据库、Redis 或 queue 不可用，也可能仍然返回 ready。

### 3. worker 双重 health 暴露

worker 当前同时存在：

- 一个共享 health controller
- 一个 `AppController` 中的静态 `/health`

这会让同一路径存在重复语义，后续维护和排查都会混乱。

## 修正原则

### 1. 统一规范端点

API 与 worker 都应统一暴露：

- `GET /health`
- `GET /health/live`
- `GET /health/ready`

其中：

- `live`
  - 只表示进程是否还活着
- `ready`
  - 表示该运行时是否可以安全接收流量或处理任务
- `health`
  - 返回更完整的检查聚合结果

### 2. 应用级 readiness 必须由应用自己定义

共享 `libs/observability` 只提供基础 health helper 和默认 service。

真正的 readiness 应由应用运行时自己定义，因为：

- API 和 worker 的关键依赖并不完全相同
- readiness 是部署语义，不是纯共享库语义

因此推荐：

- API 定义自己的 health service 或 wrapper
- worker 定义自己的 health service 或 wrapper

## 建议的最小依赖检查

### API readiness

至少应覆盖：

- 数据库可用
- Redis 可用
- queue 连接或最小可用状态

### Worker readiness

至少应覆盖：

- Redis / queue 可用
- worker 自身关键依赖可用
- 若 worker 当前已依赖数据库运行，也应纳入数据库检查

本次 change 不要求一口气把所有外部依赖都纳入，但至少要比“只看进程活着”更真实。

## 代码落位建议

推荐保持：

- `libs/observability`
  - 提供 `HealthHelper`、基础 `HealthService`
- `apps/api`
  - 提供 API 自己的 health controller 和 app-specific readiness 组合
- `apps/worker`
  - 提供 worker 自己的 health controller 和 app-specific readiness 组合

不建议：

- 继续把应用级 readiness 逻辑写回共享库默认实现
- 在 `AppController` 中再保留一个语义不同的临时 `/health`

## 测试与文档

本次 change 必须同步覆盖：

- 路由路径验证
- readiness 在关键依赖异常时的返回行为
- README 中健康检查端点说明

这样才能确保“文档写的是一套，实际跑出来又是另一套”的问题不再出现。
