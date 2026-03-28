# Delta for Mobile Auth

## ADDED Requirements

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
