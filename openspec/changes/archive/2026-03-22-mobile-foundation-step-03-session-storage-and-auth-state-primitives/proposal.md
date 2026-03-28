# 变更提案：Mobile Foundation Step 03 会话存储与认证状态原语

## 为什么要做

在 app shell 与 request pipeline 建立之后，mobile 端仍然缺少一个最小但稳定的本地会话 owner。

如果没有这一步：

- 路由层无法判断用户是未登录、已恢复会话还是本地快照损坏
- 请求层没有统一的会话读取入口
- 后续 auth feature 容易把 token、snapshot 和清理语义散落到页面或 service 里

因此需要在真正写手机号登录、refresh、协议确认之前，先把会话存储和最小认证状态原语独立落下来。

## 本次变更包含什么

本次变更聚焦移动端会话存储与认证状态原语，范围包括：

- 建立受控的本地 session snapshot 模型与存储抽象
- 建立最小 auth state owner 与启动恢复语义
- 为路由层和请求层提供统一的会话读取与清理入口
- 为本地快照损坏、字段缺失或非法状态提供受控清理路径

## 本次变更不包含什么

本次变更不包含以下内容：

- 手机号登录页面
- 验证码校验提交
- refresh token 网络调用
- 协议确认页面
- 设备会话页面

## 预期结果

完成后，项目应具备以下结果：

1. mobile 端有受控的本地 session snapshot 存储抽象
2. 启动时可以把本地快照推导为最小 auth state
3. 路由层和请求层有统一的会话读取与清理入口
4. 本地快照损坏不会直接把页面或请求层拖进崩溃分支

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/core`
- `apps/mobile/lib/app`
- `apps/mobile/README.md`
