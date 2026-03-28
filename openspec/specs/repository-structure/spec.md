# Repository Structure Specification

## Purpose

本规格定义“能干”项目当前 monorepo 的稳定目录落位与分层边界。

它只描述当前仓库结构真相源和稳定放置规则，不承担 change 工作流、提交节奏、README 更新流程或实现步骤。
## Requirements
### Requirement: 仓库必须采用稳定的 monorepo 顶层布局

系统必须使用单一 monorepo 来组织可部署运行时、共享层、契约产物、基础设施和规格真相源。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

当前受治理的顶层目录至少包括：

- `apps/`：可部署运行时
- `libs/`：服务端共享运行时能力
- `packages/`：跨运行时共享契约与生成产物
- `docs/`：当前开发者说明与运维文档
- `doc/`：原始需求、目录蓝图和早期参考材料
- `prisma/`：关系型 schema 与 migration 真相源
- `infra/`：基础设施脚本与部署资产
- `test/`：跨应用测试资产
- `openspec/`：当前规格与 change 提案

#### Scenario: 放置可部署运行时

- WHEN 仓库新增或调整一个可部署运行时
- THEN 该运行时必须放在 `apps/` 下
- AND 运行时代码不得长期放入 `libs/` 或 `packages/`

#### Scenario: 放置开发者说明

- WHEN 仓库新增面向当前开发的架构、运行或操作说明
- THEN 该说明必须放在 `docs/` 下
- AND 不应与原始需求材料混放

#### Scenario: 保留原始需求与早期蓝图

- WHEN 团队需要保留原始需求文档、目录骨架或其他早期参考材料
- THEN 这些材料必须放在 `doc/` 下
- AND 它们不得被误当作当前系统行为真相源

### Requirement: 仓库必须统一当前运行时命名

当前标准应用名称必须统一为： The system MUST satisfy the behavior, scope, and constraints described in this requirement.

- `mobile`
- `api`
- `admin-web`
- `worker`
- `agent-runtime-mock`

#### Scenario: 文档或脚本引用应用运行时

- WHEN 仓库文档、脚本或规格引用某个当前运行时
- THEN 它们必须使用上述统一名称
- AND 不得为同一运行时长期保留多套并行命名

### Requirement: 仓库必须分离共享运行时服务与共享契约

系统必须明确区分 `libs/` 与 `packages/` 的职责边界。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `libs/` 负责运行时共享服务、module、port、adapter、utility 与供应商接线
- `packages/` 负责跨运行时共享的 schema、payload、OpenAPI、proto 和其他契约产物
- 空目录、空文件或仅有占位命名的结构，不得被视为已经可复用的共享层

#### Scenario: 放置共享运行时能力

- WHEN 某项能力需要被多个服务端运行时复用，且本质是运行时模块或适配层
- THEN 它必须放在 `libs/` 下
- AND 不应长期散落在某个单一应用目录中

#### Scenario: 放置跨运行时共享契约

- WHEN API、worker、runtime 或前端需要共享同一份 payload、schema 或协议契约
- THEN 这些契约必须放在 `packages/` 下
- AND 不应长期作为单一应用的私有文件存在

### Requirement: Agent runtime 边界相关资产必须保留固定落位

系统必须将 Agent runtime 相关能力拆分为独立运行时、API 侧共享通信层和共享 runtime 契约。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

当前固定落位至少包括：

- `apps/agent-runtime-mock`：当前本地 runtime 服务端替身
- `libs/agent-runtime`：API 侧共享通信层
- `packages/agent_runtime_contracts`：task / event / error / proto 真相源

其中：

- `packages/platform_action_contracts` 负责更高层的平台动作契约
- `packages/event_schema` 负责更高层的平台事件 envelope
- 它们不替代 runtime contract 真相源

#### Scenario: API 发起 Agent runtime 调用

- WHEN `apps/api` 需要发起聊天、内容生成、训练或其他 Agent runtime 请求
- THEN 它必须通过 `libs/agent-runtime` 接入 runtime
- AND 不得在业务模块中长期直接维护 app-local transport 代码

#### Scenario: 多个 runtime 实现共享契约

- WHEN 当前 mock runtime 与其他等价 runtime 实现需要对齐调用边界
- THEN 它们必须共享 `packages/agent_runtime_contracts` 中的统一契约
- AND 不得长期维护多份彼此漂移的 task / event / error / proto 定义

### Requirement: 仓库必须为数据库 schema、HTTP contract 和 runtime contract 保留单一真相源

系统必须为关系型数据库 schema、HTTP contract 和 Agent runtime contract 分别定义单一真相源。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

当前真相源落位必须包括：

- `prisma/`：关系型 schema 与 migration 真相源
- `packages/api_contracts/openapi/openapi.json`：从 API 真相源导出的共享 HTTP contract 产物
- `packages/agent_runtime_contracts`：runtime task / event / error / proto 真相源

#### Scenario: 演进数据库结构

- WHEN 贡献者需要修改关系型数据结构
- THEN 这些变化必须先落在 `prisma/`
- AND `libs/database` 或应用目录不得并行演化出另一份 schema 真相源

#### Scenario: 生成共享 HTTP contract

- WHEN API 请求或响应契约发生变化
- THEN 共享 OpenAPI 产物必须从 API 真相源重新导出
- AND 消费端不得把派生产物反向当作原始接口定义来源

#### Scenario: 演进 runtime 契约

- WHEN API 与 runtime 之间的 task、event、error 或 proto 契约发生变化
- THEN 这些变化必须先在 `packages/agent_runtime_contracts` 中统一更新
- AND API 共享通信层与 runtime 实现都必须围绕同一份契约对齐

### Requirement: 仓库必须区分 Agent runtime 执行链路与平台后台队列链路

系统必须将 Agent runtime 执行链路与平台内部非 AI 后台队列链路视为两条不同边界。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

当前分层应保持为：

- Agent runtime 链路：`apps/api` -> `libs/agent-runtime` -> runtime 服务
- 平台后台队列链路：`apps/api` -> `libs/queue` -> `packages/job_contracts` -> `apps/worker`

#### Scenario: 分发平台后台任务

- WHEN API 需要分发通知、索引刷新、聚合或其他非 AI 后台任务
- THEN 它必须通过队列链路投递显式 job
- AND worker 必须通过共享 job contract 消费这些任务

#### Scenario: 发起 Agent 协作请求

- WHEN API 需要发起聊天、内容生成、训练或其他 Agent 执行请求
- THEN 它不得默认将该请求映射为 `apps/worker` 的平台后台 job
- AND 这类请求必须通过独立的 Agent runtime 边界进入执行层

### Requirement: 仓库必须让 Prisma schema 与已提交 migration 历史保持同步

系统必须让 `prisma/schema.prisma` 与仓库中已提交的 migration 历史保持同步，避免在关系型结构已经进入当前 schema 后仍缺失对应 migration。 The system MUST keep the Prisma schema and committed migration history aligned whenever relational structures change.

#### Scenario: 提交新的关系型结构

- WHEN 一个 change 在 `prisma/schema.prisma` 中新增或实质修改 enum、table、index、foreign key 或等价关系型结构
- THEN 仓库必须同时提交与之对应的 migration 历史
- AND 不得只依赖当前 schema 文件表达目标数据库状态

#### Scenario: 校验 schema 与 migration 是否漂移

- WHEN 贡献者对关系型结构完成一次 change 收口
- THEN 仓库必须能够通过 drift 校验确认当前 schema 与已提交 migration 历史一致
- AND 不得把存在明显漂移的状态视为可交付结果

