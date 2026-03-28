# 任务拆解：Public Content Step 16 互动信号回归护栏加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `fix/public-content-step-16-interaction-signal-regression-guards` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/public-content-step-16-interaction-signal-regression-guards` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 public-content 互动信号的回归护栏，不混入新的 signal 类型、事件持久化或 OpenAPI 导出主题
- [x] 阅读 `reports/api/public-content/app-api-public-content-review-v2.md`、`public-content-step-11-interaction-signal-and-summary-projection` / `step-13` 归档结果与当前 interactions tests，确认缺口集中在成功路径 signal 断言

## 2. 行为信号护栏补齐

- [x] 为 comments 成功创建路径补齐 `POST_COMMENTED` 或等价 signal 断言，核对动作类型、目标对象与关键 metadata
- [x] 为 follows 成功关注路径补齐 `AGENT_FOLLOWED` 或等价 signal 断言，核对动作类型、目标 Agent 与当前用户关联
- [x] 为 reports 成功提交路径补齐代表性的举报 signal 断言，核对 action、targetType、targetId 与关键 metadata

## 3. 测试辅助层整理

- [x] 对齐 comments / follows / reports 测试中的 `BehaviorSignalService` mock 或 helper，避免断言只为了让测试编译通过而失去保护价值
- [x] 核对当前 signal helper API（`emitPostSignal`、`emitAgentSignal`、`emit`）的使用面，确保新增断言围绕真实调用点而不是理想化接口

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 执行 interactions 相关 targeted jest 或等价验证，确认 signal 断言补齐后仍保持绿色
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/public-content-step-16-interaction-signal-regression-guards` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- 说明：`series/public-content -> dev` 不在本 change 内执行，该操作由人工负责
