# 任务拆解：Analytics Part1 Step 05 Raw Event Migration 与 Generated Client 收口

## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/analytics-part1` 切出 `fix/analytics-part1-step-05-raw-event-migration-and-generated-client-closure` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/analytics-part1-step-05-raw-event-migration-and-generated-client-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [ ] 确认当前 step 只收口 raw event migration 与 generated client 一致性，不混入事件口径对齐、来源语义或 duplicate 并发语义
- [ ] 阅读 `analytics-part1` step-02 / step-03、`prisma/README.md` 与 `reports/api/analytics-part1/app-api-analytics-part1-review-v1.md`，确认当前 migration 缺口和 generated client 验收缺口

## 2. Schema 与 migration 收口

- [ ] 为 `AnalyticsEventSource`、`AnalyticsRawEvent` 及其唯一约束 / 索引补齐正式 Prisma migration，使原始事件存储锚点可在新环境落库
- [ ] 校对 migration 与 `prisma/schema.prisma` 当前定义保持一致，不留下 schema 与 migration 漂移

## 3. Generated client 与测试闭环

- [ ] 收口 analytics 相关代码和单测对 generated Prisma client 的引用，确保 `pnpm db-generate` 后 runtime 与测试读取到同一份 analytics contract
- [ ] 如果本 step 改变了 analytics 验收时对 `db-generate` 的依赖表达，补齐相关测试说明或 Prisma 文档中的最小执行说明

## 4. 验证与测试

- [ ] 执行 analytics 相关最小验收链，至少覆盖 migrate / generate / 定向 analytics 测试中的关键路径；如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
- [ ] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [ ] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误

## 5. 合并与收口

- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/analytics-part1-step-05-raw-event-migration-and-generated-client-closure` merge 回 `series/analytics-part1`，保留实现分支上的阶段性提交历史
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
