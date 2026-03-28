# 变更提案：Auth Step 04 会话令牌与刷新机制

## Why / 为什么要做

完成验证码校验与账号识别后，auth 仍然缺少真正可用的登录态。

现有 [auth spec](/home/ccyd/workspace/nenggan/openspec/specs/auth/spec.md) 已明确要求：

- 登录成功后签发 access token 与 refresh token
- 建立设备会话
- access token 失效后支持刷新
- refresh token 无效时拒绝刷新

如果不把会话签发与 refresh 机制单独收敛出来，后续协议 gating、设备会话管理和退出登录都会缺少稳定凭证边界。

因此需要用一个独立 step，把登录态与刷新机制完整接起来。

## What Changes / 本次变更包含什么

本次变更聚焦登录态与刷新机制，范围包括：

- 基于已验证 auth 结果签发 access token 与 refresh token
- 建立 refresh token 持久化与轮换 / 撤销规则
- 创建或更新设备会话记录
- 实现 refresh 接口或等价服务
- 建立受保护接口识别当前用户的最小 auth runtime 接线

## 本次变更不包含什么

本次变更不包含以下内容：

- 协议确认 gating
- 设备会话列表和移除接口
- 更复杂的异常设备识别策略
- 第三方登录

## 预期结果

完成后，项目应具备以下结果：

1. 验证码登录成功后能够建立真正可用的登录态
2. access token 失效后能够通过 refresh token 刷新
3. refresh token 撤销或失效后能够拒绝刷新
4. 后续设备会话管理与退出登录可以围绕稳定会话模型继续推进

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/auth`
- auth 令牌签发与刷新逻辑
- `prisma/` 中会话模型的实际使用方式
- 受保护接口的当前用户识别接线
