# 设计说明：Auth Step 06 设备会话管理与退出登录

## 目标

这个 step 要把会话从“可签发”推进到“可治理”。

主要动作只有三个：

1. 列表化查看设备会话
2. 撤销指定设备会话
3. 退出当前设备

## 依赖

- 复用 `auth-step-01-data-model-baseline` 的会话模型
- 复用 `auth-step-04-session-token-and-refresh` 的会话签发与刷新边界

## 建议流程

### 查看设备列表

```text
authenticated user
    ->
query auth sessions by user
    ->
return manageable device session info
```

### 移除指定设备

```text
authenticated user
    ->
verify session ownership
    ->
revoke target session
    ->
subsequent refresh denied
```

### 退出当前设备

```text
authenticated user
    ->
revoke current session
    ->
current refresh token no longer valid
```

## 失败场景

- 用户不应移除不属于自己的会话
- 已撤销会话不应继续刷新
- 设备列表不应暴露超出治理所需的敏感细节
