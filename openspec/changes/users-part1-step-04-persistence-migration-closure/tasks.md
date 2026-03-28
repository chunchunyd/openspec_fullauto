# 任务拆解：Users Part1 Step 04 持久化 migration 收口

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/users-part1` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/users-part1` 切出 `fix/users-part1-step-04-persistence-migration-closure` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `fix/users-part1-step-04-persistence-migration-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 阅读 `users-part1-step-01-profile-data-model-and-self-read-baseline`、`users-part1-step-03-preferences-and-notification-settings-baseline` 与 `openspec/specs/repository-structure/spec.md`，确认本 step 只处理持久化历史收口

## 2. Migration 回补

- [ ] 2.1 审阅当前 `prisma/schema.prisma` 中 users-part1 已进入主线的资料字段与 `UserSettings` 结构，明确本 step 只补齐已存在结构的 migration 历史
- [ ] 2.2 为 `User.nickname`、`User.avatar`、`User.bio`、`User.settings` 关系与 `UserSettings` 宿主生成正式 Prisma migration，并确保索引、唯一约束和外键与当前 schema 对齐
- [ ] 2.3 如需补充说明，同步更新 `prisma/README.md` 或等价说明，标明这是 users-part1 的持久化收口而不是新字段扩张

## 3. Drift 校验

- [ ] 3.1 执行等价于 `prisma migrate diff` 的 drift 校验，确认 `prisma/schema.prisma` 与已提交 migration 历史一致
- [ ] 3.2 执行 `pnpm db-generate` 或等价验证，确认 Prisma client 生成链路保持可用
- [ ] 3.3 如条件允许，补一次基于 migration 的空库初始化验证，确认新环境可重建 users-part1 当前数据结构

## 4. 验证与收口

- [ ] 4.1 按 `docs/eslint-style-notes.md` 的当前约定确认本 step 若仅涉及 schema / migration / README 产物，则 ESLint 验收不适用并记录原因
- [ ] 4.2 按 `docs/tsc-fix-summary.md` 的当前约定确认本 step 不引入新的 TypeScript 类型回归；若只受 users 范围外共享依赖阻塞，记录 blocker
- [ ] 4.3 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [ ] 自动化将 `fix/users-part1-step-04-persistence-migration-closure` merge 回 `series/users-part1`，保留实现分支上的阶段性提交历史

- 说明：`series/users-part1 -> dev` 不在本 change 内执行，该操作由人工负责
