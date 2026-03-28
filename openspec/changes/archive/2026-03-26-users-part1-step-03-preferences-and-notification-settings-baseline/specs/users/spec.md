# Delta for Users

## ADDED Requirements

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
