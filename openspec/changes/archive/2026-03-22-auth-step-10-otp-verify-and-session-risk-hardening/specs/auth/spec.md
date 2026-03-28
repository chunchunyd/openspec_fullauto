# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须在验证码校验成功后继续执行最小风险判定

系统在验证码校验成功后、返回可用于建立登录态的认证结果前，必须继续执行最小风险判定，而不是仅依赖发码阶段的风险限制。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 验证码正确但请求命中高风险判定

- WHEN 客户端提交正确验证码，但该请求在校验阶段命中受控定义下的高风险条件
- THEN 系统必须对该请求施加受控限制或受控拒绝
- AND 系统不得仅因为验证码正确就直接放行后续登录建立

### Requirement: 系统必须在会话建立前执行最小风险判定

系统在真正创建设备会话并签发登录态前，必须再次执行最小风险判定，以避免高风险请求在最后一步无条件获得登录态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 登录态建立前命中高风险判定

- WHEN 客户端已经完成验证码校验，但请求在会话建立阶段命中受控定义下的高风险条件
- THEN 系统必须拒绝或限制该次会话建立
- AND 系统不得为该请求签发新的有效登录态

### Requirement: 系统必须为 verify 与 session 风险分支记录最小结构化上下文

系统在验证码校验阶段或会话建立阶段命中风险限制 / 风险拒绝时，必须记录最小结构化上下文，以支持排查并保持敏感信息最小暴露。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: verify 或 session 阶段命中风险分支

- WHEN auth 请求在验证码校验阶段或会话建立阶段命中风险限制或风险拒绝
- THEN 系统必须记录最小结构化上下文
- AND 日志不得直接泄露完整手机号、验证码或完整 token
