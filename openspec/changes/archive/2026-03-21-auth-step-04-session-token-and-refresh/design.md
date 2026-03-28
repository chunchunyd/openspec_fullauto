# 设计说明：Auth Step 04 会话令牌与刷新机制

## 目标

这个 step 要把“已验证身份结果”转成真正可用的登录态。

它解决的问题是：

1. 怎么签发 access token / refresh token
2. 怎么让 refresh token 与设备会话绑定
3. 怎么处理刷新、轮换和撤销

## 依赖

- 复用 `auth-step-01-data-model-baseline` 的会话模型
- 复用 `auth-step-03-otp-verify-and-user-bootstrap` 产出的已验证 auth 结果

## 建议流程

```text
verified auth result
    ->
create or update auth session
    ->
sign access token
    ->
sign refresh token
    ->
persist refresh token fingerprint / status
    ->
return auth result
```

刷新流程：

```text
submit refresh token
    ->
verify signature / expiry
    ->
lookup session state
    ->
check revoked / invalid
    ->
rotate token if needed
    ->
return new auth result
```

## 边界

- access token 负责短期访问识别
- refresh token 负责续期
- 设备会话记录负责治理与撤销

不建议让 refresh token 只存在于 JWT 层而没有可治理的会话锚点，否则 step-06 会很难收敛。

## 失败场景

- refresh token 签名无效或过期时，应直接拒绝刷新
- 会话已被撤销时，不得继续刷新
- token 轮换后，旧 refresh token 不应长期保持同等有效性
