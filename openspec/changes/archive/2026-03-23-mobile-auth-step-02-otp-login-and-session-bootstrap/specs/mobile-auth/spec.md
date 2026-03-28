# Delta for Mobile Auth

## ADDED Requirements

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
