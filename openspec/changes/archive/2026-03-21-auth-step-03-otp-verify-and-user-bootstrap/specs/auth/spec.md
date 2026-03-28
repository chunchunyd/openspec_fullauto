# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须校验登录验证码并识别账号主体

系统必须在用户提交手机号和验证码后，校验该验证码是否有效，并据此识别或创建对应账号主体。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 使用正确验证码识别账号

- WHEN 用户提交已发送的手机号和有效验证码
- THEN 系统必须完成验证码校验
- AND 系统必须识别已有账号或创建最小可用账号

#### Scenario: 使用错误或失效验证码

- WHEN 用户提交错误、过期或已失效的验证码
- THEN 系统必须拒绝继续登录流程
- AND 系统必须返回可识别失败结果

### Requirement: 系统必须在验证码校验阶段执行基础失败次数控制与账号状态判断

系统必须在验证码校验阶段执行最小失败次数控制，并在识别账号后判断其状态是否允许继续进入后续会话签发流程。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 多次验证码校验失败

- WHEN 同一手机号在短时间内多次提交错误验证码
- THEN 系统必须触发基础限制

#### Scenario: 识别到受限账号

- WHEN 系统识别到对应账号处于封禁、注销或其他不可用状态
- THEN 系统必须在进入后续会话签发前拒绝该次登录
