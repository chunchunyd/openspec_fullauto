# 任务拆解：Analytics Part1 Step 06 Source-aware Ingestion Boundary

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/analytics-part1` 切出 `fix/analytics-part1-step-06-source-aware-ingestion-boundary` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/analytics-part1-step-06-source-aware-ingestion-boundary` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只补来源语义保存与 façade 封装，不混入 migration、tracking 契约对齐或 duplicate 并发语义修复
- [ ] 阅读 `analytics-part1` step-02 / step-03 / step-05 与 `reports/api/analytics-part1/app-api-analytics-part1-review-v1.md`，确认当前 `source` 丢失点位

## 2. Ingestion 契约与 façade 收口

- [ ] 为 raw ingestion 输入补齐显式 `source` 语义，并让 service / repository 写入链路完整透传
- [ ] 保持 `emitServerEvent` / `emitServerEventSafe` 作为服务端 façade，由 analytics 模块内部统一补齐 `SERVER` 来源，避免业务模块散落拼装底层来源枚举

## 3. 来源保存验证

- [ ] 为 `CLIENT` 原始事件写入、`SERVER` 原始事件写入和服务端 façade 自动带 `SERVER` 的路径补充或更新测试
- [ ] 如果本 step 需要同步补充 analytics 输入说明或模块说明，更新对应模块注释或文档，说明当前来源语义边界

## 4. 验证与测试

- [ ] 执行 analytics 相关定向验证，确认来源语义不会再静默回退为 `SERVER`；如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/analytics-part1-step-06-source-aware-ingestion-boundary` merge 回 `series/analytics-part1`，保留实现分支上的阶段性提交历史
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
