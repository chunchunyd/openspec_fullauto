# 任务拆解：Mobile Foundation Step 05 基础埋点钩子

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-foundation`
- [x] 从 `dev/mobile-foundation` 切出 `feat/mobile-foundation-step-05-foundation-telemetry-hooks`
- [x] 确认 `mobile-foundation-step-01` 至 `step-04` 已完成或达到可复用状态
- [x] 确认当前 step 只建立 foundation telemetry hooks，不混入真实第三方 SDK、完整事件字典和业务 feature 级埋点方案

## 2. Telemetry hook 边界

- [x] 定义 foundation 层最小 telemetry 接口、事件形状和适配边界
- [x] 为启动、路由分流、request 成功失败和 session 恢复预留统一 hook 点
- [x] 提供 no-op、debug 或等价本地实现，避免基础层直接耦合真实供应商 SDK

## 3. 脱敏与约束

- [x] 明确 foundation telemetry 中的敏感字段约束，不记录完整手机号、token 或原始 session snapshot
- [x] 让 foundation hook 只表达最小结构化上下文，不抢占未来业务 feature 的埋点语义

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价模块文档，说明 foundation telemetry hooks 的职责和非目标
- [x] 对事件落点、脱敏约束和 no-op 实现补必要注释

## 5. 验证与测试

- [x] 为 startup、route、request 和 session 恢复的 hook 触发补单元测试或等价验证
- [x] 验证基础层可以在不引入真实 analytics SDK 的前提下完成本地调试
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 启动、路由分流、request 成功失败和 session 恢复时，应能触发统一 telemetry hook
2. 本地开发环境下应能使用 no-op 或 debug 实现，而不依赖真实第三方 SDK
3. foundation telemetry 不应输出完整手机号、token 或原始 session snapshot

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-foundation-step-05-foundation-telemetry-hooks` squash merge 回 `dev/mobile-foundation`
- [x] 不在本 change 内执行 `dev/mobile-foundation -> dev`，该操作由人工负责
