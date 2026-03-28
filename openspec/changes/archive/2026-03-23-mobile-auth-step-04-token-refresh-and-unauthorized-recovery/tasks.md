# 任务拆解：Mobile Auth Step 04 Token Refresh 与未授权恢复

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-auth`
- [x] 从 `dev/mobile-auth` 切出 `feat/mobile-auth-step-04-token-refresh-and-unauthorized-recovery`
- [x] 确认 `mobile-auth-step-03-consent-gating-and-post-login-access` 已完成或达到可复用状态
- [x] 确认当前 step 只处理 refresh 与未授权恢复，不混入设备会话管理和设置页扩展

## 2. 契约与边界确认

- [x] 阅读共享 OpenAPI 契约中的 `/auth/refresh` 响应与错误码，并对齐 mobile 的受控语义
- [x] 检查现有 auth header 注入边界能否升级为受控 refresh 流；如存在缺口，只补最小协调层
- [x] 明确 refresh 成功、不可恢复失败与并发等待三类状态，不让页面各自发明处理逻辑

## 3. Refresh 与请求恢复

- [x] 建立 refresh owner / coordinator，串行化并发 401 下的 refresh 行为
- [x] 在 refresh 成功时更新 `SessionSnapshot` 与 `AuthStateOwner`，并重放受支持请求
- [x] 在 `REFRESH_TOKEN_EXPIRED`、`INVALID_REFRESH_TOKEN`、`SESSION_REVOKED`、`SESSION_NOT_FOUND`、`TOKEN_REUSE_DETECTED` 等不可恢复结果下清理本地 session 并退出受保护空间
- [x] 为 401、refresh 成功与 refresh 失败映射统一反馈语义，避免页面层直接处理底层异常

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价 auth 文档，说明 refresh 边界、失败语义和非目标
- [x] 对 refresh 协调、并发门禁与 session 清理路径补必要注释

## 5. 验证与测试

- [x] 为 access token 过期后 refresh 成功、refresh 失败和并发 401 场景补单元测试或等价验证
- [x] 验证 refresh 失败后会清理本地 session 并退出受保护空间
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. access token 过期但 refresh token 仍有效时，受保护请求应能在 refresh 后继续完成
2. refresh token 过期、无效或已撤销时，应用应清理本地 session 并回到 auth 空间
3. 多个请求同时命中 401 时，不应出现无门禁的重复 refresh

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-auth-step-04-token-refresh-and-unauthorized-recovery` squash merge 回 `dev-mobile-auth`
- [x] 不在本 change 内执行 `dev-mobile-auth -> dev`，该操作由人工负责
