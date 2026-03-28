# 任务拆解：Auth Step 10 验证码校验与会话建立风控补齐

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/auth-step-10-otp-verify-and-session-risk-hardening` 并确认主项目工作树边界
- [x] 确认 `auth-step-09` 已归档并已合并回 `dev`
- [x] 阅读当前 `auth` spec、`auth-step-07` 归档资料与本 change 设计说明

## 2. 风险边界与契约

- [x] 为 `auth` capability 建立本次 step 的 spec delta
- [x] 明确 verify 阶段和 session 阶段各自需要带入的最小风险上下文
- [x] 明确 verify / session 阶段命中风险限制与风险拒绝时的返回边界

## 3. 验证码校验阶段补齐风控

- [x] 为 `OtpService.verifyLoginOtp()` 增加最小请求上下文输入
- [x] 在验证码比对成功后、返回 verified result 前接入风险信号采集与风险判定
- [x] 为 verify 阶段风险限制 / 风险拒绝补结构化日志与测试

## 4. 会话建立阶段补齐风控

- [x] 为 `SessionService.createSession()` 增加最小请求上下文输入
- [x] 在创建 session 与签发 token 前接入风险信号采集与风险判定
- [x] 为 session 阶段风险限制 / 风险拒绝补结构化日志与测试

## 5. 回归与验证

- [x] 运行 `auth` 相关 Jest 测试并确认 verify / session 风险分支通过
- [x] 运行 `tsc --noEmit`
- [x] 如对外错误语义或 contract 发生变化，执行 `openapi-export`

### 手动验收步骤

1. 正常请求应继续按既有 `/auth/login` 主流程工作
2. 命中 verify 阶段高风险的请求应在验证码正确时仍被受控限制或拒绝
3. 命中 session 阶段高风险的请求不得继续建立会话或签发 token
4. 风险分支日志应能保留最小排查上下文而不泄露敏感信息
