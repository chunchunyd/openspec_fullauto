# Delta for Interactions

## ADDED Requirements

### Requirement: 系统必须为公开 Agent 提供受控关注边界

系统必须为公开 Agent 提供受控关注边界，并明确拒绝对私有 Agent 建立关注关系。 The system MUST provide a controlled follow boundary for public agents.

#### Scenario: 关注公开 Agent

- WHEN 已登录用户对一个具备公开身份的 Agent 发起关注
- THEN 系统必须记录该关注关系或其等价状态结果
- AND 后续读取时必须能够反映当前用户的关注状态

#### Scenario: 关注私有 Agent

- WHEN 用户尝试关注一个不具备公开身份或不可见的 Agent
- THEN 系统必须拒绝该操作
- AND 不得把私有 Agent 混入公开关注对象范围

