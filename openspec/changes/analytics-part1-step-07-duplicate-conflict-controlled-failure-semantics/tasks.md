# 任务拆解：Analytics Part1 Step 07 Duplicate Conflict 受控失败语义收口

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/analytics-part1` 切出 `fix/analytics-part1-step-07-duplicate-conflict-controlled-failure-semantics` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/analytics-part1-step-07-duplicate-conflict-controlled-failure-semantics` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只收口 duplicate conflict 分类与 safe emitter 语义，不混入 migration、来源语义或 tracking 契约对齐
- [ ] 阅读 `analytics-part1` step-02 / step-03、当前 analytics service/repository 实现与 `reports/api/analytics-part1/app-api-analytics-part1-review-v1.md`，确认 duplicate 被误归类为 storage failure 的路径

## 2. Duplicate conflict 分类收口

- [ ] 识别 raw event 写入中的唯一约束冲突，并将其映射为 duplicate 语义，而不是真实存储故障
- [ ] 收口 `emitServerEventSafe` 对 duplicate conflict 的返回值、错误码和日志级别，让 duplicate 与真实 storage failure 可观测地区分开

## 3. 失败路径测试

- [ ] 为预检查命中 duplicate、数据库唯一约束冲突 duplicate、safe emitter duplicate 返回和真实 storage failure 返回补充或更新测试
- [ ] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 4. 验证与测试

- [ ] 执行 analytics 定向验证，确认 duplicate conflict 不再被误报成 storage infrastructure failure
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/analytics-part1-step-07-duplicate-conflict-controlled-failure-semantics` merge 回 `series/analytics-part1`，保留实现分支上的阶段性提交历史
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
