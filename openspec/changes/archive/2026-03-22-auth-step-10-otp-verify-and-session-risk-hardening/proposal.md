# 变更提案：Auth Step 10 验证码校验与会话建立风控补齐

## 为什么要做

`auth-step-09` 已经把公开登录主路径、手机号规范化、refresh 错误语义和 HTTP 集成测试收紧了一轮，但完整复核后仍剩下一个高优先级问题：

- `auth` 当前的风险信号与风险判定主要只接在验证码发送链路
- `verifyLoginOtp()` 和 `createSession()` 仍然没有接入等价的风险评估或最小风险留痕

这和已归档的 `auth-step-07-risk-hardening` 目标并不完全一致。现在的实际结果是：

- 明显异常的请求在发码时可能被限制或拒绝
- 但一旦验证码已经到手，异常请求仍可能直接穿过验证码校验并建立会话

这会削弱前面几个 auth step 的安全闭环，也会让“auth 已具备最小风控能力”这个结论打折扣。

因此需要一个新的小 step，把剩余的风控缺口补齐在验证码校验和会话建立两个阶段，而不是重做整套风控系统。

## 本次变更包含什么

本次变更聚焦 auth 剩余风控缺口，范围包括：

- 为验证码校验链路接入最小风险信号收集与风险判定
- 为会话建立链路接入最小风险信号收集与风险判定
- 明确风险限制、风险拒绝和正常放行在 verify / session 阶段的行为边界
- 为命中风险分支补结构化日志与错误上下文
- 补充 verify / session 风险分支的测试覆盖

## 本次变更不包含什么

本次变更不包含以下内容：

- 重做现有发送链路风控逻辑
- 引入完整设备指纹平台或多维度风控中心
- 重做验证码缓存、token 签发或会话模型
- 一次性统一全站审计日志体系
- 新增第三方登录或更多认证方式

## 预期结果

完成后，项目应具备以下结果：

1. 风险判定不再只停留在发码阶段，而会覆盖验证码校验与会话建立
2. 高风险请求即使拿到 OTP，也不能无条件建立登录态
3. auth 风险限制与风险拒绝分支会有最小可排查日志上下文
4. verify / session 风险行为会有自动化测试兜底

## 影响范围

本次变更主要影响：

- `apps/api/src/modules/auth/otp.service.ts`
- `apps/api/src/modules/auth/session.service.ts`
- `apps/api/src/modules/auth/risk.service.ts`
- `apps/api/src/modules/auth/__tests__/otp.service.spec.ts`
- `apps/api/src/modules/auth/__tests__/session.service.spec.ts`
- 如对外错误语义变化时对应的 `packages/api_contracts/openapi/openapi.json`
