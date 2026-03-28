# Delta for Users

## ADDED Requirements

### Requirement: 系统必须在 users 自我资料与设置写入入口上执行受控请求校验

系统必须在 users 自我资料与设置写入入口上执行受控请求校验，并在进入持久化前拒绝非白名单字段、错误类型或未受支持的受控取值。 The system MUST enforce controlled request validation on self profile and self settings write endpoints before persistence.

#### Scenario: 提交非白名单或 auth-owned 字段

- WHEN 已登录用户向 `PATCH /users/me` 或 `PATCH /users/me/settings` 提交非白名单字段、auth-owned 字段或其他未开放键
- THEN 系统必须在写入前拒绝该请求
- AND 不得把这些字段静默吞掉后继续当作成功更新处理

#### Scenario: 提交错误类型或未受支持的受控取值

- WHEN 已登录用户向 self profile 或 self settings 写入入口提交错误类型、非法 URL、非法布尔值或未受支持的语言枚举
- THEN 系统必须返回稳定可解释的校验失败结果
- AND 不得把无效值传递到持久化层或业务主状态更新路径
