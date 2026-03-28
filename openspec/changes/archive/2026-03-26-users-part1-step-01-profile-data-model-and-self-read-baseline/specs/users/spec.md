# Delta for Users

## ADDED Requirements

### Requirement: 系统必须为已登录用户提供受控的自我资料读取边界

系统必须为已登录用户提供受控的自我资料读取边界，并将认证主状态与可编辑资料主数据分开处理。 The system MUST provide a controlled self-profile read boundary for authenticated users.

#### Scenario: 读取自己的资料

- WHEN 已登录用户请求读取自己的资料
- THEN 系统必须返回受控的基础资料结果
- AND 返回结果必须能够区分显式值与允许缺省的资料字段

#### Scenario: 认证字段与资料字段分层

- WHEN 平台返回用户自我资料
- THEN 系统必须避免把仅属于 auth 的内部状态直接暴露为 users 资料字段
- AND users 模块必须能够独立承载后续资料扩展
