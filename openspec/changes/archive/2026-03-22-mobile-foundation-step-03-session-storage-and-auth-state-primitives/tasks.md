# 任务拆解：Mobile Foundation Step 03 会话存储与认证状态原语

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-foundation`
- [x] 从 `dev/mobile-foundation` 切出 `feat/mobile-foundation-step-03-session-storage-and-auth-state-primitives`
- [x] 确认 `mobile-foundation-step-02-http-contract-and-request-pipeline` 已完成或达到可复用状态
- [x] 确认当前 step 只建立 session snapshot、storage abstraction 与最小 auth state owner，不混入手机号登录、refresh 网络调用和协议 gating 页面

## 2. 会话快照与本地存储抽象

- [x] 定义受控的本地 session snapshot 结构、版本与最小字段边界
- [x] 建立 secure storage 或等价实现的统一抽象，明确 key owner、读写入口和清理语义
- [x] 为缺字段、损坏或明显非法的本地快照建立受控清理路径

## 3. 最小 auth state owner

- [x] 建立最小 auth state owner，用于表达启动恢复中、无可用会话和存在可用会话等受控状态
- [x] 让路由层与 request pipeline 可以消费该状态，而不是各自独立读取本地存储
- [x] 提供统一的清理会话与回到未登录边界的入口

## 4. 设计说明与模块文档

- [x] 补 `design.md`，说明 session snapshot、auth state owner 和启动恢复路径之间的边界关系
- [x] 更新 `apps/mobile/README.md` 或等价模块文档，说明 storage abstraction 与 auth state owner 的职责

## 5. 验证与测试

- [x] 为 snapshot 读写、损坏清理和状态推导补单元测试或等价验证
- [x] 为启动恢复后的路由分流补 widget 测试或等价验证
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 人工写入一份合法 session snapshot 后，应用启动应进入受控的已恢复登录边界
2. 人工写入一份损坏 snapshot 后，应用启动应清理本地数据并回到未登录边界
3. 清理会话入口触发后，路由层与请求层都应回到统一的未登录状态

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-foundation-step-03-session-storage-and-auth-state-primitives` squash merge 回 `dev/mobile-foundation`
- [x] 不在本 change 内执行 `dev/mobile-foundation -> dev`，该操作由人工负责
