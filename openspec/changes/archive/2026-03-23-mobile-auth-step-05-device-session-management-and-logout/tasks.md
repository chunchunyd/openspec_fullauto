# 任务拆解：Mobile Auth Step 05 设备会话管理与退出登录

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-auth`
- [x] 从 `dev/mobile-auth` 切出 `feat/mobile-auth-step-05-device-session-management-and-logout`
- [x] 确认 `mobile-auth-step-04-token-refresh-and-unauthorized-recovery` 已完成或达到可复用状态
- [x] 确认当前 step 只处理设备会话管理与退出登录，不混入账号注销或更大范围的设置中心改造

## 2. 契约与边界确认

- [x] 阅读共享 OpenAPI 契约中的 `/auth/sessions`、`/auth/sessions/remove` 和 `/auth/logout`
- [x] 确认设备会话列表与当前设备 logout 都复用已建立的 authenticated request 与 refresh 边界
- [x] 明确"移除其他设备"和"退出当前设备"是两条不同受控动作，不在页面层混写

## 3. 设备会话与退出登录

- [x] 建立设备会话列表入口，展示当前设备标记、最近活跃时间和设备基础信息
- [x] 接入 `/auth/sessions/remove`，允许用户移除非当前设备会话，并映射后端业务错误
- [x] 接入 `/auth/logout`，在成功或等价不可恢复状态下清理本地 session 并退出受保护空间
- [x] 通过统一反馈原语处理加载、空态、失败与重试，不让设置页直接暴露底层错误

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价 auth 文档，说明设备会话治理与当前设备 logout 边界
- [x] 对当前设备判定、session 清理与退出收口补必要注释

## 5. 验证与测试

- [x] 为设备会话列表、移除其他设备、当前设备 logout 和失败映射补单元测试或 widget 测试
- [x] 验证当前设备 logout 后会清理本地 session 并退出受保护空间
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 已登录用户应能查看自己的设备会话列表，并识别当前设备
2. 移除其他设备会话后，页面应更新对应列表状态
3. 当前设备执行 logout 后，应用应清理本地 session 并返回 auth 空间

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-auth-step-05-device-session-management-and-logout` squash merge 回 `dev/mobile-auth`
- [x] 不在本 change 内执行 `dev/mobile-auth -> dev`，该操作由人工负责
