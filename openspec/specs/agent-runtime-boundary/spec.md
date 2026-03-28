# Agent Runtime Boundary Specification

## Purpose

本规格定义“能干”项目首期 Agent runtime 边界的当前行为真相源。

首期 Agent runtime boundary 能力聚焦于：

- 区分平台 API 控制面与 runtime 执行面
- 通过统一共享通信层与共享契约接入 runtime
- 让本地 mock runtime 与其他等价 runtime 实现共享同一调用边界
- 以统一任务与事件语义回流运行结果
- 约束 runtime 访问平台能力的方式

## Requirements

### Requirement: 系统必须区分平台控制面与 runtime 执行面

系统必须将平台 API 与 Agent runtime 视为不同职责层，而不是把 Agent 执行逻辑长期内嵌在业务模块或平台后台任务执行器中。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

平台 API 负责：

- 鉴权与归属校验
- 可见性与业务状态校验
- 创建或关联统一任务
- 消费运行事件并投影业务结果

runtime 负责：

- prompt 编排
- 模型路由
- 上下文装配
- 工具调用
- 执行过程与结果事件输出


#### Scenario: 平台发起一次 Agent 协作请求

- WHEN 聊天、内容生成、训练或其他业务流程需要让 Agent 执行一次协作
- THEN 平台 API 必须先完成平台侧校验并通过统一 runtime 边界发起请求
- AND 不得在业务模块中直接内嵌执行引擎职责

#### Scenario: runtime 完成一次执行

- WHEN runtime 完成一次 Agent 协作请求
- THEN 它必须回流任务状态和事件结果
- AND 业务实体的最终状态投影必须由平台侧完成

### Requirement: 系统必须通过统一共享通信层与共享契约接入 runtime

系统必须通过统一共享通信层与共享 runtime contract 接入 Agent runtime，而不是让每个业务模块分别维护本地 transport 接线。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

当前正式链路默认以共享 proto + gRPC provider 为主；兼容性 HTTP 通道可以存在，但不得被视为长期正式边界。


#### Scenario: API 接入本地 mock runtime

- WHEN 平台在本地开发环境接入 mock runtime
- THEN 它必须沿用统一共享通信层与共享 runtime contract
- AND 不应为 mock 单独发明一套与正式链路长期漂移的调用边界

#### Scenario: 切换到另一种等价 runtime 实现

- WHEN 平台从本地 mock runtime 切换到另一种等价 runtime 实现
- THEN 调用方必须能够继续沿用同一份共享 runtime contract
- AND 业务模块不应因为 provider 替换而直接依赖新的底层 transport 细节

### Requirement: 平台侧必须在进入 runtime 前完成调用校验

所有 Agent 调用都必须在进入 runtime 前完成平台侧鉴权、归属、可见性和必要的业务状态校验。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 用户登录态校验
- Agent 所属权或公开可见性校验
- 目标业务对象存在性与可操作状态校验
- 幂等键或等价重复调用控制


#### Scenario: 用户请求自己的私有 Agent 协作

- WHEN 用户向自己的私有 Agent 发起聊天、生成或训练请求
- THEN 平台必须先校验该用户对该 Agent 的操作权限
- AND 校验通过后才能进入 runtime 调用流程

#### Scenario: 用户请求无权限的 Agent 协作

- WHEN 用户尝试对不具备访问条件的私有 Agent 发起协作请求
- THEN 平台必须在进入 runtime 前拒绝该请求
- AND runtime 不应承担这类业务归属判断的主职责

### Requirement: runtime 回流必须通过统一任务与事件边界表达

系统必须让 runtime 通过统一任务状态和 append-only 事件回流执行结果，而不是直接把业务状态修改命令反推给平台。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 聊天任务产生流式输出

- WHEN runtime 在执行聊天任务过程中产生渐进式输出
- THEN 它必须通过统一事件边界回流流式结果
- AND 平台必须基于这些事件更新自己的会话与消息视图

#### Scenario: 内容生成任务成功完成

- WHEN runtime 成功生成一份内容结果
- THEN 它必须回流任务成功状态与相关结果事件
- AND 平台必须据此决定帖子应落为草稿、待审核或其他业务状态

### Requirement: runtime 访问平台能力时必须通过受控 action / tool 边界

runtime 如需访问平台能力，必须通过受控的 action / tool contract 进行，而不是直接绕过平台边界访问数据库或内部 service。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

这些调用必须受到权限、策略和治理控制，关键结果必须可追踪。


#### Scenario: runtime 请求平台能力

- WHEN runtime 在执行过程中需要读取知识、写入草稿、追加审计或调用其他平台能力
- THEN 它必须通过受控 action / tool 边界发起请求
- AND 不得直接依赖平台内部数据库连接或 app-local service

#### Scenario: 平台治理规则阻止高风险调用

- WHEN 某次 action / tool 调用命中权限、风控或策略限制
- THEN 平台必须能够拒绝该调用或返回受控错误结果
- AND 该结果必须能够影响对应任务状态、事件或业务投影
