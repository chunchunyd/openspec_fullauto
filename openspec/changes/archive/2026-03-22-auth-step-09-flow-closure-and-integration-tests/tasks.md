# 任务拆解：Auth Step 09 主流程收口与集成测试补强

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/auth-step-09-flow-closure-and-integration-tests` 并确认主项目工作树边界
- [x] 确认 `auth-step-08` 已归档，当前实现以其加固后的 controller / guard / DTO 为基线
- [x] 阅读当前 `auth` spec、本 change 设计说明，以及最新 auth review 结论

## 2. 契约与边界收口

- [x] 为 `auth` capability 建立本次 step 的 spec delta
- [x] 明确并记录公开 OTP 登录主路径的边界，避免继续公开暴露半流程 HTTP 入口
- [x] 明确 auth 内部手机号 canonical format 与可接受输入格式
- [x] 明确 refresh token 的最小错误语义拆分

## 3. 实现公开流程收口

- [x] 收敛 `/auth/login` 为当前公开 OTP 登录主入口
- [x] 调整 `/auth/otp/verify` 的公共暴露方式，使其不再形成”消耗 OTP 但无法建立登录态”的对外半流程
- [x] 保持 service 层 `verifyLoginOtp()` 可复用于登录主流程，而不是把控制器层逻辑耦死

## 4. 实现手机号与 refresh 语义补强

- [x] 更新手机号规范化逻辑，使 auth 入口接受常见大陆手机号格式并统一归一为 `11` 位内部格式
- [x] 对齐相关单测与 DTO 示例，避免 repository / cache / controller 各自使用不同手机号格式
- [x] 调整 refresh token 校验错误分支，至少区分 `REFRESH_TOKEN_EXPIRED` 与 `INVALID_REFRESH_TOKEN`
- [x] 如公共 contract 变化，执行 `openapi-export`

## 5. 补 auth HTTP 集成测试

- [x] 新增聚焦 auth 的 HTTP 集成测试文件，使用 Nest app + `supertest` 验证 controller / pipe / guard 行为
- [x] 覆盖 `/auth/login` 的成功、业务失败与请求校验失败场景
- [x] 覆盖 `/auth/refresh` 的成功、expired 与 invalid 场景
- [x] 覆盖受保护接口在缺失 token、revoked session、正常会话下的 HTTP 行为

## 6. 验证与回归

- [x] 运行 `auth` 相关 Jest 测试并确认新增 HTTP 集成测试稳定通过
- [x] 运行 `tsc --noEmit`
- [x] 如 `openapi` 有变更，确认导出产物与 controller 行为一致

### 手动验收步骤

1. 使用 `+86 138 0013 8000`、`138-0013-8000`、`13800138000` 请求 auth 入口时，应都能归一到同一内部手机号
2. 客户端应能明确识别 `/auth/login` 为公开 OTP 登录主入口，不再被公开半流程接口误导
3. 无 token、坏 token、已撤销会话访问受保护接口时，应返回明确 401
4. refresh token 过期与无效时，应返回不同业务错误码
