# 任务拆解：Analytics Part1 Step 02 原始事件接收与存储锚点

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/analytics-part1` 切出 `feat/analytics-part1-step-02-raw-event-ingestion-and-storage-anchor` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/analytics-part1-step-02-raw-event-ingestion-and-storage-anchor` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 `analytics-part1-step-01-event-dictionary-and-tracking-doc-baseline`、`openspec/specs/analytics/spec.md` 与 `openspec/specs/audit-log/spec.md`，确认原始事件写入不会与审计记录 owner 冲突
- [x] 检查现有事件字典、`packages/api_contracts` 与潜在共享日志接线能力是否可复用，确认本 step 不需要额外拆分新的共享契约前置 change
- [x] 进一步确认 `analytics-part1` 在本 step 只补原始事件接收与存储锚点，不混入看板报表、复杂聚合或客户端批量接入

## 2. 接收契约与存储模型

- [x] 设计并落最小原始事件接收契约、上下文字段和 append-only 存储锚点
- [x] 约束必填上下文、异常输入拒绝和去重或等价保护，避免无上下文脏数据进入存储

## 3. 模块与写入入口

- [x] 初始化 `apps/api/src/modules/analytics/*` 的最小 module/service/repository 或等价写入路径
- [x] 为后续 step-03 的服务端 emitter 预留统一写入入口，避免业务模块直接散落拼装原始事件
- [x] 为事件接收成功、拒绝和存储失败补齐必要的结构化日志与错误上下文，避免后续只能依赖调试日志反推问题

## 4. 验证与测试

- [x] 为合法事件写入、最小上下文缺失拒绝、异常输入拒绝和存储写入失败降级补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/analytics-part1-step-02-raw-event-ingestion-and-storage-anchor` squash merge 回 `series/analytics-part1`
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
