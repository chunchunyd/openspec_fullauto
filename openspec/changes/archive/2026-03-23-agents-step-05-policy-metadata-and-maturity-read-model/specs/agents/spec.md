# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须维护 Agent 平台侧策略 metadata

系统必须维护 Agent 平台侧策略 metadata，以支撑 owner 管理、公开流程前置判断和后续 runtime 消费边界。 The system MUST maintain platform-side agent policy metadata for controlled management and downstream consumption.

#### Scenario: owner 读取当前策略 metadata

- WHEN Agent owner 查看某个 Agent 的管理详情
- THEN 系统必须返回该 Agent 当前生效的策略 metadata
- AND 调用方不应依赖 runtime 私有实现细节才能获取这些管理信息

#### Scenario: owner 更新策略 metadata

- WHEN Agent owner 提交合法的策略 metadata 更新
- THEN 系统必须保存更新后的平台侧策略元数据
- AND 后续管理读取必须返回最新生效结果

### Requirement: 系统必须返回可被公开流程消费的 Agent 成熟度结果

系统必须返回可被公开流程消费的 Agent 成熟度结果，以避免公开申请前长期依赖模糊人工判断。 The system MUST return an agent maturity result that can be consumed by downstream publication workflows.

#### Scenario: 读取 Agent 成熟度

- WHEN owner 或平台侧流程需要判断某个 Agent 的成熟度
- THEN 系统必须返回该 Agent 的当前成熟度结果或等价读模型
- AND 该结果必须能够被后续公开申请边界稳定消费

