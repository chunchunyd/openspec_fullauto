# 设计说明：Auth Step 02 验证码发送与冷却控制

## 目标

这个 step 只解决“发码”问题：

1. 手机号归一化
2. 验证码生成
3. 短期缓存
4. 短信发送
5. 冷却与基础发送频控

## 依赖

- 复用 `auth-step-01-data-model-baseline` 的用户基础模型
- 复用 `libs/cache`
- 复用 `libs/sms`

## 建议流程

```text
client request
    ->
normalize phone
    ->
check cooldown / send limit
    ->
generate otp
    ->
write cache
    ->
send sms
    ->
return cooldown metadata
```

## 缓存边界

验证码发送建议在 auth 模块自己的缓存目录下维护语义，而不是把业务 key 直接塞进 `libs/cache`。

至少需要区分：

- 验证码正文缓存
- 发送冷却状态
- 发送频控计数

敏感标识应优先使用 hash 后的手机号摘要。

## API contract 边界

如果本 step 对外暴露发送验证码接口：

- contract 真相源仍在 `apps/api`
- 共享依据应通过 `packages/api_contracts/openapi/openapi.json` 导出
- 前端不应长期依据临时字段约定接入

## 失败场景

- 频控命中时，不应继续发送短信
- 冷却期内重复请求时，不应重新生成新验证码
- 短信 provider 失败时，应给出可识别失败结果，并避免留下难以解释的缓存状态
