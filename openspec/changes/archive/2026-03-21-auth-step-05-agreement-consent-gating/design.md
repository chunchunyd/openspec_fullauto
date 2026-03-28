# 设计说明：Auth Step 05 协议确认与准入阻塞

## 目标

这个 step 关注的是“能不能进入完整产品能力”，而不是“是不是已经通过认证”。

建议把它视为认证成功后的准入 gating：

- 身份可以已经被识别
- 会话可以已经建立
- 但若必要确认未完成，系统仍不应放行完整产品能力

## 依赖

- 复用 `auth-step-01-data-model-baseline` 的协议确认记录
- 复用 `auth-step-04-session-token-and-refresh` 的登录态边界

## 建议流程

```text
authenticated user
    ->
read consent records
    ->
if missing required consent
    -> return gated auth result
else
    -> allow full product access
```

确认流程：

```text
submit required consent
    ->
persist consent records
    ->
mark gating resolved
    ->
subsequent login no longer blocked
```

## 失败场景

- 用户未确认必要协议时，不得被视为可直接进入完整产品能力
- 已确认用户后续登录时，不应重复阻塞主流程
- 确认写入失败时，不应误报用户已经通过 gating
