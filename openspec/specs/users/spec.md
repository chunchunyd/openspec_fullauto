# users Specification

## Purpose
TBD - created by archiving change users-part1-step-01-profile-data-model-and-self-read-baseline. Update Purpose after archive.
## Requirements
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

### Requirement: 系统必须为已登录用户提供受控的偏好与通知设置边界

系统必须为已登录用户提供受控的偏好与通知设置边界，并为未显式配置的字段提供明确默认值语义。 The system MUST provide a controlled preferences and notification settings boundary for authenticated users.

#### Scenario: 读取当前有效设置

- WHEN 已登录用户读取自己的偏好与通知设置
- THEN 系统必须返回当前有效的设置结果
- AND 对未显式配置的字段必须提供可解释的默认值

#### Scenario: 局部更新设置

- WHEN 已登录用户局部更新受支持的设置项
- THEN 系统必须只更新对应字段或其等价结果
- AND 不得因为局部更新无意覆盖其他未提交设置

### Requirement: 系统必须允许已登录用户受控更新自己的资料

系统必须允许已登录用户受控更新自己的资料，并只接受明确白名单中的可编辑字段。 The system MUST allow authenticated users to update their own profiles through a controlled boundary.

#### Scenario: 更新可编辑资料字段

- WHEN 已登录用户提交受支持的资料字段更新
- THEN 系统必须保存该更新或其等价结果
- AND 后续自我读取必须返回更新后的受控资料

#### Scenario: 尝试修改非资料归属字段

- WHEN 用户尝试通过 users 写入 auth-owned 身份字段或未开放字段
- THEN 系统必须拒绝该写入
- AND 不得让资料更新入口越权修改认证主状态

