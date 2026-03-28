# 任务拆解：Public Content Step 05 Agent 切换器边界

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-05-agent-switcher-boundary` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/feed/spec.md`、`openspec/specs/agents/spec.md` 与默认首页 feed 实现
- [x] 确认当前 step 只建立 Agent 切换边界，不混入复杂混排和互动聚合

## 2. 切换器结果与输入边界

- [x] 为首页返回可切换 Agent 列表、当前选中 Agent 摘要和切换输入参数的受控契约
- [x] 限定只允许切换到当前用户可消费、可见的 Agent 视角

## 3. 切换后的 feed 读取

- [x] 让 feed 在切换 Agent 后返回对应视角下的新结果，而不是继续复用上一视角的列表

## 4. 验证与测试

- [x] 为默认 Agent 列表返回、切换成功、不可切换 Agent 拒绝和切换后结果刷新补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-05-agent-switcher-boundary` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

