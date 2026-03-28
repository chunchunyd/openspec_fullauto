# 任务拆解：Analytics Part1 Step 03 服务端发射器与非阻塞写入边界

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/analytics-part1` 切出 `feat/analytics-part1-step-03-server-side-emitter-and-nonblocking-write-boundary` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/analytics-part1-step-03-server-side-emitter-and-nonblocking-write-boundary` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 `analytics-part1-step-01-event-dictionary-and-tracking-doc-baseline`、`analytics-part1-step-02-raw-event-ingestion-and-storage-anchor` 与当前已具备业务主线的 `auth`、`agents`、`agreements` 模块，确认首批服务端接线点
- [x] 检查现有 analytics 写入入口、`packages/api_contracts` 与共享日志接线能力是否可复用，确认本 step 不把 emitter 逻辑散落到业务模块
- [x] 进一步确认 `analytics-part1` 在本 step 只建立服务端 emitter 与少量代表性接线，不混入全量模块覆盖、聚合任务或后台看板

## 2. 发射边界与失败处理

- [x] 抽象统一的 server-side emitter 或等价写入 facade，复用 step-02 的原始事件接收与存储入口
- [x] 为事件发射补充最小上下文装配、错误记录和非阻塞降级策略
- [x] 为事件发射成功、拒绝和下游写入失败补齐必要的结构化日志与错误上下文

## 3. 代表性接线

- [x] 在当前已实现的核心服务端流程中接入首批代表性事件发射点，例如 `auth`、`agents` 的成功、拒绝和失败路径
- [x] 确保业务调用方不直接散落拼装 analytics 原始写入细节

## 4. 验证与测试

- [x] 为发射成功、写入失败不阻塞主流程、上下文缺失兜底和代表性接线补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `feat/analytics-part1-step-03-server-side-emitter-and-nonblocking-write-boundary` squash merge 回 `series/analytics-part1`
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
