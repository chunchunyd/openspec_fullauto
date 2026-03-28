# 任务拆解：Analytics Part1 Step 01 事件字典与 Tracking 文档基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/analytics-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/analytics-part1` 切出 `feat/analytics-part1-step-01-event-dictionary-and-tracking-doc-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `feat/analytics-part1-step-01-event-dictionary-and-tracking-doc-baseline` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
- [x] 阅读 `openspec/specs/analytics/spec.md`、`openspec/specs/audit-log/spec.md`、`openspec/specs/event-schema/spec.md` 与当前 `docs/tracking/` 现状，确认事件字典真相源位置
- [x] 检查现有 `docs/tracking/`、`openspec/specs/analytics/spec.md` 与事件定义来源是否可直接复用，确认本 step 不需要新增共享 schema 前置 change
- [x] 进一步确认 `analytics-part1` 在本 step 只补 tracking 文档基线，不混入原始事件接收、看板报表或全量模块埋点接线

## 2. 事件字典文档

- [x] 在 `docs/tracking/` 建立首期事件字典文档，定义事件命名、含义、关键属性、最小上下文和版本维护方式
- [x] 划定首批事件覆盖范围与留白规则，避免把未实现模块一次性写成不可维护的大表

## 3. 边界对齐

- [x] 明确服务端事件、客户端事件与审计记录之间的命名对齐和 owner 边界
- [x] 记录事件口径变更时的版本或修订规则，避免隐式改名导致口径漂移

## 4. 验证与校对

- [x] 校对事件名称、属性口径与版本约定，确认后续 step 可以直接复用该字典
- [x] 本 step 仅新增 tracking 文档与 spec delta，不涉及可执行 TS 代码；因此 ESLint 验收不适用，但需在变更说明中确认无代码路径被修改
- [x] 本 step 仅新增 tracking 文档与 spec delta，不涉及 TypeScript 源码；因此 TypeScript 验收不适用，但需在变更说明中确认无 TS 输入变化

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
  - 注：tracking 文档已在 commit 16785d4 提交，工作区已干净
- [x] 自动化将 `feat/analytics-part1-step-01-event-dictionary-and-tracking-doc-baseline` squash merge 回 `series/analytics-part1`
- 说明：`series/analytics-part1 -> dev` 不在本 change 内执行，该操作由人工负责
