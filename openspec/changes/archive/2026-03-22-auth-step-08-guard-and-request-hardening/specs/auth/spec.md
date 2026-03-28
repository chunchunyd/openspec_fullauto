# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须在受保护认证接口上校验 access token 与活跃会话状态

系统必须在需要登录态的认证相关接口上校验 access token 的有效性，并确认其关联会话仍处于可用状态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 缺少或无效 access token 访问受保护接口

- WHEN 客户端在未携带 access token 或携带无效 access token 的情况下访问协议确认、设备会话管理或退出登录等受保护认证接口
- THEN 系统必须拒绝该请求
- AND 系统不得返回受保护用户数据

#### Scenario: 会话已撤销后继续使用旧 access token

- WHEN 某个 access token 关联的会话已经被退出登录、移除设备会话或其他受控撤销操作标记为失效
- THEN 系统必须拒绝该 access token 继续访问受保护认证接口

### Requirement: 系统必须对 auth 接口请求执行最小运行时输入校验

系统必须对 auth 相关接口的最小必填字段、基础类型和明显非法输入执行运行时校验，避免明显坏请求直接落成未处理异常。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 缺少必填字段或字段类型错误

- WHEN 客户端向发送验证码、验证码登录、刷新登录态、协议确认或设备会话治理等 auth 接口提交缺少必填字段或字段类型错误的请求
- THEN 系统必须返回明确的请求校验失败结果
- AND 系统不得因为这类明显坏输入直接返回未处理的 500 错误
