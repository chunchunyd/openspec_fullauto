# 任务拆解：Analytics Part1 Step 04 Tracking 契约与 Emitter 对齐收口

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/analytics-part1` 切出 `fix/analytics-part1-step-04-tracking-contract-and-emitter-realignment` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/analytics-part1-step-04-tracking-contract-and-emitter-realignment` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只收口 tracking 契约与 emitter 对齐，不混入 migration、来源语义或 duplicate 并发语义修复
- [ ] 阅读 `analytics-part1` step-01 ~ step-03、`docs/tracking/*` 当前内容与 `reports/api/analytics-part1/app-api-analytics-part1-review-v1.md`，确认本 step 要消除的契约漂移点

## 2. Canonical 契约收敛

- [ ] 盘点 `auth`、`agents` 当前已接线的首批服务端事件，明确哪些事件名沿用现有字典，哪些字段需要回归统一口径，哪些稳定事件需要正式补入字典
- [ ] 为“同一业务语义的成功 / 拒绝 / 失败”确定统一顶层事件名与结果字段约定，避免继续用多套事件名表达同一条业务主线

## 3. 文档、规格与 emitter 对齐

- [ ] 更新 `docs/tracking/event-dictionary.md`，让当前已接线事件的名称、关键字段和版本说明与真实实现对齐
- [ ] 更新 `docs/tracking/metrics-definition.md` 与 analytics spec delta，确保指标口径和 requirement 只引用当前真实存在且稳定的事件契约
- [ ] 调整 `auth`、`agents` 中当前 emitter 调用点及对应 analytics 测试，移除“文档事件名”和“代码事件名”并存的状态

## 4. 验证与测试

- [ ] 为至少一条 `auth` 事件和一条 `agents` 事件补充或更新契约对齐测试；如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/analytics-part1-step-04-tracking-contract-and-emitter-realignment` merge 回 `series/analytics-part1`，保留实现分支上的阶段性提交历史
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
