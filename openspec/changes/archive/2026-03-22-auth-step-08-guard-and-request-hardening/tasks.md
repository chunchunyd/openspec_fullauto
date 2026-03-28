# 任务拆解：Auth Step 08 鉴权守卫与请求校验加固

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/auth-step-08-guard-and-request-hardening` 并确认主项目工作树边界
- [x] 阅读当前 `auth` spec、`api-contracts` spec 和本 change 设计说明
- [x] 确认本 step 只收敛 auth 的守卫、访问控制、请求校验与检查噪音，不混入验证码或会话主流程重写

## 2. 鉴权守卫与会话校验

- [x] 为 `auth` capability 建立本次 step 的 spec delta
- [x] 在 `auth` 模块中注册并接线 `AuthGuard`
- [x] 仅为 `consent`、设备会话和退出登录等受保护接口显式挂上 `@UseGuards(AuthGuard)`
- [x] 让 access token 校验在验证 JWT 之外,同时校验关联 session 仍处于 active 状态
- [x] 确认已撤销或已失效 session 对应的 access token 不再访问受保护接口

## 3. 请求校验与契约

- [x] 为 `auth` 请求 DTO 补最小 `class-validator` 规则
- [x] 在 `auth` controller 范围内接入 `ValidationPipe` 或等价运行时输入校验
- [x] 明确缺字段、类型错误和空字符串等坏输入的失败语义,避免未处理 500
- [x] 如对外 HTTP contract 新增 400 / 401 语义或响应结构变化,执行 `openapi-export` 并确认共享契约产物更新

## 4. 检查噪音清理
- [x] 清理 `auth` 目录本轮已知的 ESLint 噪音,包括未使用 import、未使用常量和未使用类型
- [x] 对守卫和会话状态校验中的非直观逻辑补必要注释

## 5. 验证与测试
- [x] 为 `AuthGuard` 或等价鉴权接线补单元测试
- [x] 为 access token 对应 session 已撤销时的拒绝行为补测试
- [x] 为缺失 token、无效 token 和正常 token 访问受保护接口补测试
- [x] 为 auth 请求 DTO 的运行时校验补测试,确认坏输入不会直接炸成 500
- [x] 重新执行 `tsc --noEmit`、`eslint "src/modules/auth/**/*.ts"` 和 `jest src/modules/auth --runInBand`

### 手动验收步骤
1. 未携带 access token 请求 `auth/consent/*`、`auth/sessions`、`auth/logout` 等受保护接口时,应被明确拒绝
2. 正常登录后访问上述接口,应能被正确识别为当前用户
3. 当前设备退出登录或设备会话被移除后,原 access token 再访问受保护接口时,应被拒绝
4. 对 `send otp`、`login`、`refresh` 等接口提交缺字段或类型错误的 body 时,应得到明确校验失败,而不是 500
