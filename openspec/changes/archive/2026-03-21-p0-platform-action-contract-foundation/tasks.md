# 任务拆解：P0 平台动作契约基建

## 1. 契约与规格

- [x] 为 `platform-actions` capability 建立本次 change 的 spec delta
- [x] 为 `repository-structure` 建立本次 change 的 spec delta，明确平台动作契约、`ai-runtime` 反腐层和 adapter 边界
- [x] 在 proposal/design 中确认：平台动作契约不等同于 BullMQ job contract，也不等同于 mobile API contract

## 2. `packages/platform_action_contracts` 基础层

- [x] 创建 `packages/platform_action_contracts` 的最小包结构、公开入口与 README
- [x] 定义动作命名规则、请求 envelope、响应 envelope 和错误边界
- [x] 定义最小元数据字段，如 `correlationId`、`idempotencyKey`、`actor`、`source`
- [x] 定义首期 smoke action，例如 `system.ping`

## 3. `ai-runtime` / adapter 边界

- [x] 明确 `apps/api/src/modules/ai-runtime` 的职责，作为应用侧进入 AI / adapter 世界的反腐层
- [x] 明确业务模块应通过 facade 请求平台动作，而不是直接依赖 LLM client、Bull queue 或临时 CLI 参数格式
- [x] 明确 adapter 只能通过平台动作契约请求平台能力，不能直接碰数据库或平台内部 service

## 4. 与内部 transport 和事件的关系

- [x] 明确 `packages/job_contracts` 继续作为内部异步 transport 契约，而不是平台动作契约
- [x] 明确未来 `packages/event_schema` 与平台动作生命周期事件的关系
- [x] 如当前阶段不实现完整事件体系，至少保留后续拆分与迁移路径说明

## 5. 验证与文档

- [x] 为动作 envelope、错误边界或 smoke action contract 的关键逻辑补单元测试或等价验证
- [x] 更新 `packages/platform_action_contracts/README.md`
- [x] 如开发入口或架构说明发生变化，更新根 README 或相关架构文档
- [x] 对”平台动作契约 vs 内部 Bull job 契约”的边界补必要注释或模块说明
