# 设计说明：Auth Step 03 验证码校验与账号识别

## 目标

这个 step 解决两件事：

1. 校验验证码是否可信
2. 把可信验证码映射到一个明确的账号主体

它不负责最终 token 签发，但会为下一步会话签发提供稳定输入。

## 依赖

- 复用 `auth-step-01-data-model-baseline` 的用户状态模型
- 复用 `auth-step-02-otp-send-and-cooldown` 的验证码缓存与发送语义

## 建议流程

```text
submit phone + otp
    ->
load cached otp state
    ->
check expired / invalid / consumed
    ->
check failed attempts
    ->
match otp
    ->
find or create user
    ->
check account status
    ->
return verified auth result
```

## 结果边界

这里建议产出一个受控的 auth 领域结果，例如：

- 已验证用户 ID
- 手机号归一化结果
- 校验通过时间
- 可供下一步会话签发使用的最小上下文

这样下一步在做 token / session 时，不需要重新混入验证码校验逻辑。

## 失败场景

- 验证码错误、过期或已失效时，必须返回可识别失败结果
- 多次失败时，必须触发基础限制
- 账号处于封禁或不可用状态时，不得继续进入后续会话签发
- 成功校验后，应避免同一验证码被重复作为有效输入长期复用
