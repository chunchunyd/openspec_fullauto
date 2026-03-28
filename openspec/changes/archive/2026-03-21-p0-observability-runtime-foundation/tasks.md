# 任务拆解：P0 服务端可观测性基建

## 1. 契约与规格

- [x] 为 `observability` capability 建立本次 change 的 spec delta
- [x] 在 proposal/design 中确认：服务端共享 observability 范围、mobile 边界、queue / job 上下文接线原则
- [x] 明确本次 change 不承载完整移动端日志实现、不承载 analytics / BI

## 2. `libs/observability` 共享运行时基础层

- [x] 整理 `libs/observability` 的可复用包结构、公开入口与 README
- [x] 定义统一 `ObservabilityModule` 与共享 logger 接线方式
- [x] 定义 request / job 上下文模型及其最小注入方式
- [x] 明确错误日志、关键状态日志与脱敏规则

## 3. API / worker 接线

- [x] 明确 `apps/api` 的请求日志接线方式，例如 interceptor / middleware / filter 的职责边界
- [x] 明确 `apps/worker` 的 job 日志接线方式,覆盖开始、成功、失败和重试上下文
- [x] 明确 queue / scheduler 后续应如何复用共享 logger，而不是各自继续输出散落日志
- [x] 明确 correlation id 在请求链路与异步链路中的透传原则

## 4. health / readiness

- [x] 设计共享 health helper 与应用级 health controller 的边界
- [x] 明确 `api` 与 `worker` 需要暴露的最小 health / readiness 行为
- [x] 如果 health 暂时不做完整自动化检查，保留可重复执行的手动验收步骤

## 5. 验证、测试与文档

- [x] 为共享 logger / context helper 的关键逻辑补单元测试
- [x] 规划请求日志与 job 日志的最小验收路径
- [x] 更新 `libs/observability/README.md`
- [x] 如 health 端点、开发入口或环境变量说明发生变化，更新根 README 或相关入口文档
- [x] 对 correlation id、脱敏边界和 health 职责边界补必要注释或模块说明
