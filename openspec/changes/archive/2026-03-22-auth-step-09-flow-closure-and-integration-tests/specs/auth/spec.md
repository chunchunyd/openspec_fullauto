# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须将公开 OTP 登录入口收敛为可完成会话建立的完整流程

系统对外暴露的手机号验证码登录入口必须能够在成功消费验证码后继续完成登录态建立；系统不得将“只完成验证码校验但无法继续建立会话”的半流程作为当前首期公共登录入口。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 客户端通过公开 OTP 登录入口完成登录

- WHEN 客户端使用公开的手机号验证码登录入口提交合法手机号与有效验证码
- THEN 系统必须在成功校验后继续建立登录态或返回可继续建立登录态的受控结果
- AND 系统不得让客户端停留在已经消耗验证码但无法继续登录的状态

### Requirement: 系统必须接受常见大陆手机号输入格式并统一为单一内部格式

系统必须接受常见大陆手机号输入格式，并在进入 auth 领域后统一归一为单一内部 canonical format，以避免不同层对同一手机号产生不一致处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 使用常见大陆手机号格式请求 auth 接口

- WHEN 客户端使用 `13800138000`、`138 0013 8000`、`138-0013-8000` 或 `+86 138 0013 8000` 等常见格式请求 auth 接口
- THEN 系统必须能够识别这些输入对应的是同一个大陆手机号
- AND 系统必须在内部统一归一为同一手机号格式后再参与验证码、用户识别和会话相关逻辑

### Requirement: 系统必须区分 refresh token 过期与无效

系统在处理 refresh token 时，必须至少区分“refresh token 已过期”和“refresh token 无效或损坏”两类失败结果，避免客户端和排查流程长期依赖模糊错误语义。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: refresh token 已过期

- WHEN 客户端使用已过期的 refresh token 请求刷新登录态
- THEN 系统必须返回明确的已过期失败结果

#### Scenario: refresh token 无效或损坏

- WHEN 客户端使用格式错误、签名无效、被篡改或类型不正确的 refresh token 请求刷新登录态
- THEN 系统必须返回明确的无效 token 失败结果
