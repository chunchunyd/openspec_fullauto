# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须签发并维护可刷新的双令牌登录态

系统必须在登录成功后签发 access token 与 refresh token，并让 refresh token 受到可校验、可轮换、可撤销的会话治理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 登录成功后签发双令牌

- WHEN 用户完成受控的身份校验并被允许继续登录
- THEN 系统必须签发 access token 与 refresh token
- AND 系统必须将该结果与设备会话记录关联

#### Scenario: 使用有效 refresh token 刷新

- WHEN 客户端使用仍然有效的 refresh token 请求刷新
- THEN 系统必须返回新的可用认证结果

#### Scenario: 使用无效或已撤销 refresh token

- WHEN 客户端使用无效、过期或已撤销的 refresh token 请求刷新
- THEN 系统必须拒绝刷新
- AND 客户端必须被视为需要重新登录
