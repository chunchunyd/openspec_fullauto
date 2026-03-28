# 任务拆解：P0 BullMQ 队列基建

## 1. 契约与规格

- [x] 为 `queue` capability 建立本次 change 的 spec delta
- [x] 为 `repository-structure` 建立本次 change 的 spec delta，细化 `libs/queue`、`packages/job_contracts` 与 `apps/worker` 的职责
- [x] 在 proposal/design 中确认：BullMQ 选型、scheduler 与 queue 的边界、最小 smoke path

## 2. `libs/queue` 共享运行时基础层

- [x] 创建 `libs/queue` 的可复用包结构、公开入口与 README
- [x] 引入 `@nestjs/bullmq` 与 BullMQ 所需依赖
- [x] 实现 `QueueModule` 的最小接线，统一读取 Redis 连接配置
- [x] 提供共享 producer 封装，避免应用层直接散落底层 BullMQ 接线
- [x] 约定默认的 attempts、backoff、失败观测和基础日志接线

## 3. `packages/job_contracts` 共享任务契约

- [x] 创建 `packages/job_contracts` 的最小包结构与公开入口
- [x] 集中定义首期 queue name 与 job name 常量
- [x] 为首期 smoke job 定义共享 payload contract
- [x] 明确后续业务 job 的命名和扩展方式，避免字符串散落

## 4. `apps/api` 与 `apps/worker` 接入

- [x] 在 `apps/api` 中接入共享队列模块并验证可以投递 smoke job
- [x] 在 `apps/worker` 中接入共享队列模块并注册最小 processor
- [x] 明确 `worker.module.ts`、processor、scheduler 的目录职责
- [x] 确认 scheduler 只负责投递，不直接承载完整业务处理逻辑

## 5. 验证、测试与日志

- [x] 为 `libs/queue` 的关键辅助逻辑补单元测试
- [x] 为 smoke job 补最小集成验证，覆盖”投递成功 -> worker 消费 -> 日志可观测”
- [x] 验证失败重试或失败事件观测的基本行为
- [x] 如果当前阶段暂不补完整自动化验证，明确原因并保留可重复执行的手动验收步骤

## 6. 文档与入口说明

- [x] 更新 `libs/queue/README.md`，说明职责边界、公开入口、配置和使用方式
- [x] 更新根 README 或相关入口文档，补充队列开发入口、环境变量与 worker 使用说明
- [x] 对 queue / processor / contract 分层和重试语义补必要注释或模块说明
