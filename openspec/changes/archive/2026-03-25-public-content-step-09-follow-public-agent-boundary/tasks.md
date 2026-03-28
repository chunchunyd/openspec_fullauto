# 任务拆解：Public Content Step 09 关注公开 Agent 边界

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-09-follow-public-agent-boundary` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/interactions/spec.md`、`openspec/specs/agents/spec.md` 与公开 Agent 可见性边界
- [x] 确认当前 step 只建立关注关系边界，不混入粉丝列表和推荐策略

## 2. 关注关系边界

- [x] 为公开 Agent 关注关系补齐最小持久化锚点、幂等约束和取消关注语义
- [x] 限定只允许对公开 Agent 建立关注关系，拒绝私有 Agent 或不可见 Agent

## 3. 接口与返回结果

- [x] 建立关注与取消关注接口，并返回当前用户的最小关注状态结果

## 4. 验证与测试

- [x] 为关注公开 Agent、取消关注、重复关注幂等和关注私有 Agent 拒绝补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-09-follow-public-agent-boundary` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

