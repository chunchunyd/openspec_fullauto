# Delta for Admin

## ADDED Requirements

### Requirement: 系统必须通过已验证的后台身份读取用户列表与详情

系统必须通过已验证的后台身份读取用户列表与详情，而不是仅凭 header 存在性放行后台用户读取入口。 The system MUST require a validated admin identity context before allowing admin user list or detail reads.

#### Scenario: 已验证后台用户读取用户列表或详情

- WHEN 一个已通过后台身份校验且满足最低角色要求的后台用户读取用户列表或用户详情
- THEN 系统必须返回其被授权读取的用户结果
- AND 读取路径必须复用后台身份存在性与启用状态校验

#### Scenario: 伪造或失效后台身份尝试读取用户

- WHEN 请求方仅提供形式正确的后台 header，但后台用户不存在、已禁用或不满足最低角色要求
- THEN 系统必须拒绝该读取
- AND 不得仅凭非空 `x-admin-user-id` 暴露后台用户数据

