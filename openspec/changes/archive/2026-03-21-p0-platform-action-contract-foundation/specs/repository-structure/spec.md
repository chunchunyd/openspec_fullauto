# Delta for Repository Structure

## ADDED Requirements

### Requirement: 仓库必须为平台动作契约提供独立落位

系统必须将平台动作契约作为跨运行时、跨实现阶段的稳定能力边界单独维护，而不是混入移动端 API contract、内部 queue job contract 或某个单一应用目录。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `packages/platform_action_contracts` 负责平台动作名、请求 / 响应 envelope、错误边界与共享元数据
- `packages/job_contracts` 继续负责内部异步 transport 契约
- 两者不得长期混用为同一层语义


#### Scenario: 定义 adapter 与平台之间的动作契约

- WHEN 当前后端、CLI adapter 或未来平台内核需要围绕同一动作能力协作
- THEN 该能力契约必须放在 `packages/platform_action_contracts` 或等价独立共享契约包中维护
- AND 不得仅存在于某个 Nest 模块 DTO、Bull job payload 或临时脚本参数中

#### Scenario: 内部队列执行某个平台动作

- WHEN 平台动作在当前阶段内部通过 queue / worker 落地
- THEN 该内部 transport 契约应继续放在 `packages/job_contracts`
- AND 不得反向取代平台动作契约的独立地位

### Requirement: 仓库必须为 AI runtime 与外部 adapter 保留反腐边界

系统必须在应用运行时与外部 Agent / adapter 之间保留清晰的反腐边界，避免业务模块直接依赖临时 adapter 实现细节。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `apps/api` 中的 `ai-runtime` 负责应用层进入 AI / adapter 世界的统一入口
- Agent / adapter 不得直接依赖数据库层或平台内部服务
- 平台状态变更必须通过平台动作边界执行


#### Scenario: 业务模块请求 AI 协作能力

- WHEN 某个业务模块需要请求 AI / Agent 协作能力
- THEN 它应通过 `apps/api` 中统一的 `ai-runtime` 入口发起请求
- AND 不应在业务模块内长期散落直接调用 adapter、模型 client 或内部 transport 的实现

#### Scenario: Adapter 需要写平台状态

- WHEN 外部 adapter 需要触发平台状态变更
- THEN 它必须通过正式的平台动作边界请求平台执行
- AND 不得直接访问平台数据库或绕过平台内部校验逻辑
