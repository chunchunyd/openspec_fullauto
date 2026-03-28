# Delta for Mobile Auth

## ADDED Requirements

### Requirement: mobile 客户端必须在 access token 过期时通过受控 refresh 续期会话

mobile 客户端在 access token 过期时，必须通过受控 refresh 续期会话，而不是把所有未授权结果都直接等价成重新登录。 The mobile client MUST refresh the session in a controlled manner when the access token expires.

#### Scenario: access token 过期但 refresh 成功

- WHEN 一个受保护请求因 access token 过期命中未授权结果，且 refresh 仍可成功
- THEN mobile 客户端必须完成受控 refresh 并更新本地会话快照
- AND 受支持请求必须能够在续期后继续完成

#### Scenario: 多个请求同时命中过期

- WHEN 多个受保护请求在同一时间窗口内同时命中 access token 过期
- THEN mobile 客户端必须复用同一次受控 refresh
- AND 不得无门禁地并发发起多次 refresh

### Requirement: mobile 客户端必须在 refresh 不可恢复时清理本地会话并退出受保护空间

mobile 客户端在 refresh token 过期、无效、已撤销或出现等价不可恢复结果时，必须清理本地会话并退出受保护空间。 The mobile client MUST clear the local session and leave protected space when refresh is not recoverable.

#### Scenario: refresh 不可恢复

- WHEN `/auth/refresh` 返回过期、无效、已撤销、会话不存在或复用异常等不可恢复结果
- THEN mobile 客户端必须清理本地会话并回到 auth 空间
- AND 不得继续保留受保护访问能力
