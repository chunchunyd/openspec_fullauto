# 任务拆解：Mobile Auth Step 03 协议确认 gating 与登录后放行

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-auth`
- [x] 从 `dev/mobile-auth` 切出 `feat/mobile-auth-step-03-consent-gating-and-post-login-access`
- [x] 确认 `mobile-auth-step-02-otp-login-and-session-bootstrap` 已完成或达到可复用状态
- [x] 确认当前 step 只处理协议确认 gating 与登录后放行，不混入 refresh 和设备会话管理

## 2. 契约与边界确认

- [x] 阅读共享 OpenAPI 契约中的 `/auth/consent/status`、`/auth/consent/record` 与 `/auth/consent/record-all`
- [x] 明确 mobile 侧"存在 session"和"允许完整产品访问"是两层不同状态，不直接混写进 foundation 原语
- [x] 确认当前 step 不重写后端协议版本策略，只消费服务端当前真相

## 3. Consent Gate 与放行流程

- [x] 建立已登录但未完成协议确认时的正式 consent gate 页面或等价边界
- [x] 在登录成功后与启动恢复后拉取 `/auth/consent/status`，据此决定 gated 或 full access 路由
- [x] 接入 `/auth/consent/record-all` 或受控单项确认流，完成首期必要协议确认
- [x] 在协议全部完成后切换到完整产品可达空间；在部分失败或请求失败时保持 gated 边界与可重试入口

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价 auth 文档，说明 session、gated 和 full access 三层边界
- [x] 对 gating 拉取、协议确认与放行路由条件补必要注释

## 5. 验证与测试

- [x] 为启动恢复后的 gating 拉取、协议确认成功、部分失败和重试补单元测试或 widget 测试
- [x] 验证未完成协议确认的 session 不会被直接放入完整产品空间
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 登录成功但缺协议确认的用户，应进入 consent gate 而不是完整产品空间
2. 启动恢复后，如服务端仍返回未放行，应用应继续停留在 gated 边界
3. 完成必要协议确认后，应用应能稳定放行到完整产品入口

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-auth-step-03-consent-gating-and-post-login-access` squash merge 回 `dev/mobile-auth`
- [x] 不在本 change 内执行 `dev/mobile-auth -> dev`，该操作由人工负责
