# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须允许已登录用户创建私有 Agent 并查看自己的 Agent 列表

系统必须允许已登录用户创建私有 Agent，并以 owner-scoped 方式查看自己的 Agent 列表，而不是要求后续功能在没有“我的 Agent”基线的前提下各自造入口。 The system MUST allow authenticated users to create private agents and list their own agents through an owner-scoped boundary.

#### Scenario: 创建私有 Agent

- WHEN 已登录用户提交合法的最小 Agent 创建信息
- THEN 系统必须为该用户创建一个新的私有 Agent
- AND 新建 Agent 不得默认直接进入公开可见状态

#### Scenario: 查看我的 Agent 列表

- WHEN 已登录用户请求查看自己的 Agent 列表
- THEN 系统必须只返回该用户拥有的 Agent 结果
- AND 列表结果必须包含足以支撑后续选择和管理的最小基础资料

