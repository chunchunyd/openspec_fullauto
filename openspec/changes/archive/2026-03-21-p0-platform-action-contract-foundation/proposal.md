# 变更提案：P0 平台动作契约基建

## 为什么要做

当前仓库已经逐步补起了数据库、缓存、队列、短信、可观测性和对象存储等共享基础设施，但“AI 能力究竟通过什么稳定边界接入平台”这件事，仍然没有在代码或 OpenSpec 中被正式定义。

这会直接带来一个结构性风险：

- 现在如果继续往前做 `auth`、`agents`、`content` 或更多 AI 功能，很容易自然演变成“业务模块 -> Bull job / LLM client / 临时 adapter”这样的直连模式
- 一旦这样长开，未来从“现有后端 + Agent + CLI adapter”迁移到“原生 AI-native 平台内核”时，就会发现大家实际上依赖的是一堆 Nest/Bull/内部 DTO 细节，而不是稳定的平台动作契约

目前你们已经对路线形成了共识：

- 前期先走“现有后端 + Agent + CLI adapter”的可验证路线
- 后期逐步把验证过的 action / tool 能力收敛进更原生的平台内核
- 真实的数据库读写、状态变更和权限校验，长期不应由 Agent 或 adapter 直接执行

要让这条路线真正可落地，第一步不是再多写几个 Agent job，而是先定义一层稳定的“平台动作契约”和“AI runtime / adapter 边界”。

## 本次变更包含什么

本次变更聚焦于平台动作契约和 AI runtime 边界，范围包括：

- 定义 `packages/platform_action_contracts` 的职责边界，明确其负责平台动作名、请求/响应 envelope、错误边界与共享元数据
- 明确这层契约必须是 transport-neutral 的，不应直接等同于 BullMQ job 名称、Nest DTO 或某个临时 CLI 参数格式
- 定义 `apps/api` 中 `ai-runtime` 的职责边界，明确其作为应用层进入 AI / adapter 世界的反腐层
- 明确 Agent / CLI adapter 只能通过平台动作契约请求平台能力，而不能直接碰数据库或平台内部服务
- 定义首期最小 smoke action，用于验证契约与边界，而不是一上来就绑定具体业务能力
- 要求同步补齐 README、必要注释和相关入口文档

## 本次变更不包含什么

本次变更不包含以下内容：

- Go 平台内核本身的实现
- Connect RPC / gRPC 的完整实现接线
- CLI adapter 的完整实现
- 全量业务动作的一次性定义
- 具体 Agent 工作流、内容生成策略或工具编排逻辑

## 预期结果

完成后，项目应具备以下结果：

1. 仓库中存在一套独立于 BullMQ 和 Nest DTO 的平台动作契约层
2. `apps/api` 中存在明确的 `ai-runtime` / adapter 反腐层边界
3. 后续 Agent、CLI adapter 和未来 Go 平台内核都可以围绕同一套平台动作模型演进
4. 数据库读写、状态变更和权限校验必须由平台侧动作执行，而不是由 Agent 或 adapter 直接绕过
5. 后续业务 change 不再把内部 queue/job 命名误当成长期平台能力契约

## 影响范围

本次变更主要影响：

- 新增的 `platform-actions` capability
- `repository-structure` 中与 `packages/`、`apps/api`、Agent / adapter 边界相关的约束
- `apps/api/src/modules/ai-runtime` 的长期职责定位
- 未来 CLI adapter、Agent 编排层与原生平台内核的迁移路径
