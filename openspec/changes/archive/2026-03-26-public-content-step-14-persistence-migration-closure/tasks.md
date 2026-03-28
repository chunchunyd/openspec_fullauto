# 任务拆解：Public Content Step 14 持久化 migration 收口

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `chore/public-content-step-14-persistence-migration-closure` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `chore/public-content-step-14-persistence-migration-closure` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 Prisma migration 交付，不混入新的 schema 扩张、HTTP contract 返工或互动行为改造
- [x] 阅读 `reports/api/public-content/app-api-public-content-review-v2.md`、当前 `prisma/schema.prisma` 与 `prisma/migrations/`，确认本 step 只回补 public-content 已落地结构对应的 migration 历史

## 2. Migration 回补

- 人类提示：数据库内容目前为空，如果有冲突难以解决，直接删掉所有migrations文件，重新生成!
- [x] 为 comments、follows、likes、favorites、reports 相关 enums / tables / indexes / foreign keys 生成正式 Prisma migration，并避免重写既有 archived step 的业务语义
- [x] 核对 migration 覆盖当前 schema 中已落地的 public-content 结构，确认新环境可以通过 migration 获得与现状一致的数据库结构

## 3. Drift 校验

- [x] 执行等价于 `prisma migrate diff` 的校验，确认已提交 migration 历史与当前 `prisma/schema.prisma` 不再漂移
- [x] 执行 `pnpm db-generate` 或等价验证，确认 migration 回补后 Prisma client 生成链路保持可用

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 的当前约定确认本 step 仅涉及 Prisma schema / migration 产物，ESLint 验收不适用并记录原因
- [x] 按 `docs/tsc-fix-summary.md` 的当前约定确认本 step 不涉及 TypeScript 源码行为变更，TypeScript 验收不适用并记录原因
- [x] 如果本 step 新增或修改 migration / schema 说明文件，补充必要注释或 README 说明，明确这是 public-content 持久化历史回补而不是新能力扩张

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `chore/public-content-step-14-persistence-migration-closure` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- 说明：`series/public-content -> dev` 不在本 change 内执行，该操作由人工负责
