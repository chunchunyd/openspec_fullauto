# mobile-auth Specification

## Purpose
TBD - created by archiving change mobile-auth-step-01-login-entry-and-otp-send. Update Purpose after archive.
## Requirements
### Requirement: mobile 客户端必须以手机号验证码作为首期公开认证入口

mobile 客户端必须以手机号验证码作为首期公开认证入口，并停止把“注册占位页”继续当作与后端主路径并行的真实能力。 The mobile client MUST expose phone OTP login as the primary public authentication entrypoint for the first release.

#### Scenario: 用户进入认证入口

- WHEN 用户从 public 空间进入认证入口
- THEN mobile 客户端必须展示手机号验证码登录主路径
- AND 不得继续让注册占位页对当前首期流程形成误导性分流

### Requirement: mobile 客户端必须对验证码发送结果提供受控反馈

mobile 客户端必须通过共享 HTTP contract 对验证码发送结果提供受控反馈，包括成功、冷却、频控和风险限制，而不是把原始 transport 错误直接暴露给页面。 The mobile client MUST provide controlled feedback for OTP send results through the shared HTTP contract.

#### Scenario: 验证码发送成功

- WHEN 用户提交合法手机号并成功请求验证码
- THEN mobile 客户端必须展示受控的成功反馈与冷却倒计时
- AND 不得允许用户在冷却期间无门禁地重复发送

#### Scenario: 验证码发送失败

- WHEN `/auth/otp/send` 返回冷却、频控、风险限制或等价失败结果
- THEN mobile 客户端必须展示与该业务结果对齐的受控反馈
- AND 不得把底层 HTTP 库原始异常直接当作最终用户提示

### Requirement: mobile 客户端必须消费验证码登录结果并建立可恢复的本地会话

mobile 客户端必须消费 `/auth/login` 的验证码登录结果，并将成功结果映射为可恢复的本地会话，而不是停留在一次性页面状态。 The mobile client MUST consume the OTP login result and establish a restorable local session.

#### Scenario: 验证码登录成功

- WHEN 用户提交合法手机号与有效验证码并登录成功
- THEN mobile 客户端必须写入可恢复的本地会话快照并更新认证状态 owner
- AND 后续应用启动必须能够恢复同一最小已登录状态

#### Scenario: 验证码登录失败

- WHEN `/auth/login` 返回验证码错误、风控限制或账号受限等失败结果
- THEN mobile 客户端必须展示与该业务结果对齐的受控反馈
- AND 不得把用户留在“提交已完成但状态不明”的模糊页面状态

### Requirement: mobile 客户端必须在登录成功但 gating 未放行时保持受控访问边界

mobile 客户端在登录成功但 `gating.canAccessFullProduct=false` 时，必须保持受控访问边界，而不是直接放行进入完整产品空间。 The mobile client MUST keep a controlled access boundary when login succeeds but full-product access is still gated.

#### Scenario: 登录成功但仍缺协议确认

- WHEN `/auth/login` 成功返回 tokens，但 `gating.canAccessFullProduct=false`
- THEN mobile 客户端必须进入受控的 gated pending 边界
- AND 不得把用户直接导入完整产品可达路由

### Requirement: mobile 客户端必须在已登录但未满足协议确认时保持 consent gate

mobile 客户端在已登录但未满足必要协议确认时，必须保持 consent gate，而不是仅凭存在 session 就直接放行完整产品空间。 The mobile client MUST keep users behind a consent gate until required agreements are confirmed.

#### Scenario: 启动恢复后仍缺必要确认

- WHEN 应用恢复到一个存在可用 session 的用户，并从服务端得到“仍缺必要协议确认”的 gating 结果
- THEN mobile 客户端必须继续停留在 consent gate
- AND 不得因为本地已有 session 就默认放行进入完整产品空间

### Requirement: mobile 客户端必须通过受控流程完成必要协议确认后再放行完整产品

mobile 客户端必须通过受控流程完成必要协议确认，并在服务端确认放行后才进入完整产品空间。 The mobile client MUST complete required consents through a controlled flow before granting full-product access.

#### Scenario: 完成全部必要协议确认

- WHEN 用户在 consent gate 中完成所有必要协议确认，且服务端返回放行结果
- THEN mobile 客户端必须将用户导入完整产品可达空间
- AND 后续启动恢复必须能够依据服务端当前 gating 真相继续保持该放行结果

#### Scenario: 协议确认部分失败

- WHEN 协议确认请求出现部分失败、网络失败或服务端仍未放行
- THEN mobile 客户端必须保持用户停留在 consent gate 并提供受控重试入口
- AND 不得把部分成功误判为完整放行

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

### Requirement: mobile 客户端必须允许用户查看并管理设备会话

mobile 客户端必须允许已登录用户查看并管理设备会话，包括识别当前设备与移除其他设备会话。 The mobile client MUST allow signed-in users to view and manage device sessions.

#### Scenario: 查看设备会话列表

- WHEN 已登录用户进入设备会话管理入口
- THEN mobile 客户端必须展示设备会话列表、当前设备标记和基础设备信息
- AND 不得把原始后端响应直接暴露为未加工数据结构

#### Scenario: 移除其他设备会话

- WHEN 用户请求移除一个非当前设备的会话
- THEN mobile 客户端必须通过受控流程调用会话移除接口并更新页面结果
- AND 不得把“移除其他设备”与“退出当前设备”混成同一个动作

### Requirement: mobile 客户端必须支持当前设备退出登录并清理本地会话

mobile 客户端必须支持当前设备退出登录，并在退出后清理本地会话与受保护访问能力。 The mobile client MUST support logging out the current device and clearing the local session.

#### Scenario: 当前设备退出登录

- WHEN 已登录用户在当前设备执行退出登录
- THEN mobile 客户端必须清理本地会话并退出受保护空间
- AND 后续不得继续把该设备视为已登录状态

