# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须支持 Agent owner 提交公开申请并读取当前申请状态

系统必须支持 Agent owner 提交公开申请并读取当前申请状态，以便后续审核流可以在稳定申请锚点上继续推进。 The system MUST allow an agent owner to submit a publication application and read its current application status.

#### Scenario: 提交公开申请

- WHEN Agent owner 为一个满足前置条件的 Agent 提交公开申请
- THEN 系统必须记录该申请结果
- AND 该 Agent 不得在未经后续受控流程前直接视为正式公开可见

#### Scenario: 读取公开申请状态

- WHEN Agent owner 查询某个 Agent 的公开申请状态
- THEN 系统必须返回当前申请状态或等价受控结果
- AND 调用方不应依赖 admin 私有实现才能判断该 Agent 是否已处于申请中

