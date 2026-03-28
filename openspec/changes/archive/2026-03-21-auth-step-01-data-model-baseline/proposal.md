# 变更提案：Auth Step 01 认证数据模型基线

## 为什么要做

当前仓库中的 `auth` 模块仍然是空骨架，而 `prisma/schema.prisma` 里也只有非常薄的 `User` 基线模型。

但现有 [auth spec](/home/ccyd/workspace/nenggan/openspec/specs/auth/spec.md) 已经明确要求：

- 用户可以通过手机号验证码登录
- 账号状态会影响登录结果
- 首次完整登录前需要判断协议确认状态
- 系统需要建立设备会话并支持后续管理

如果在没有认证数据模型基线的情况下直接推进短信发送、验证码校验和会话签发，后续很容易出现：

- 用户状态、协议确认和会话信息散落在不同实现里
- refresh token 与设备会话没有稳定持久化锚点
- 后续 step 之间反复改表、返工接口和测试

因此需要先用一个小 change，把 auth 领域的最小持久化主数据定下来。

## 本次变更包含什么

本次变更聚焦于 auth 最小数据模型基线，范围包括：

- 为用户补齐账号状态、手机号归一化所需字段或等价结构
- 建立协议确认持久化结构
- 建立设备会话与 refresh token 持久化锚点
- 明确与 `libs/database`、`prisma/` 和后续 auth step 的边界
- 同步补齐迁移、必要测试和相关 README / 模块说明

## 本次变更不包含什么

本次变更不包含以下内容：

- 短信发送或验证码缓存
- 验证码校验与用户登录流程
- access token / refresh token 的实际签发
- 设备会话列表接口、退出登录接口
- 登录风控策略本身

## 预期结果

完成后，项目应具备以下结果：

1. `auth` 后续 step 可以围绕稳定的用户状态、协议确认与会话模型继续推进
2. 账号状态限制、协议 gating 和设备会话管理有明确持久化落点
3. refresh token 持久化与撤销不必在后续 change 中临时发明
4. `prisma/` 中的 auth 主数据不再停留在占位状态

## 影响范围

本次变更主要影响：

- `prisma/schema.prisma` 与 migration
- `libs/database` 在 auth 领域的数据访问方式
- `apps/api/src/modules/auth` 的领域模型和服务骨架
- 后续 `auth-step-02` 到 `auth-step-07` 的实现路径
