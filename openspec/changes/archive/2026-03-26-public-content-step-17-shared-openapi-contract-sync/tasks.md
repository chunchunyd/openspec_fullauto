# 任务拆解：Public Content Step 17 共享 OpenAPI 契约收口

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `chore/public-content-step-17-shared-openapi-contract-sync` 实现分支，并将当前 worktree 绑定到该分支
- 说明：在进入实现分支前不进行任何实现性编辑是执行原则，非可勾选任务
- 说明：续跑或接手已有 worktree 时的现场检查是执行原则，非可勾选任务
- [x] 确认当前 step 只收口 public-content 的共享 OpenAPI 导出，不混入新的 public API 行为扩张或 runtime 契约修改
- [x] 阅读 `reports/api/public-content/app-api-public-content-review-v2.md`、`api-contracts` 当前 spec、`infra/scripts/openapi-export.sh` 与 public-content 相关 controller，确认需要进入共享契约产物的路径清单

## 2. 共享契约导出

- [x] 执行 `openapi-export` 或等价导出流程，刷新 `packages/api_contracts/openapi/openapi.json` 与 `docs/api/*`
- [x] 核对 public-content 已交付的 feed、content public detail、comments、follows、reports 代表性路径都已进入共享 OpenAPI 产物

## 3. Spot Check

- [x] 对导出后的代表性成功 / 错误契约做最小 spot check，确认共享产物没有继续遗漏关键 public-content 路径
- 说明：导出流程成功，无需记录阻塞原因

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 的当前约定确认本 step 只涉及共享契约产物与导出链路，ESLint 验收不适用并记录原因
- [x] 按 `docs/tsc-fix-summary.md` 的当前约定确认本 step 不涉及 TypeScript 行为源码变更，TypeScript 验收不适用并记录原因
- [x] 保留本 step 的导出命令与核对结果，确保接手者可以重复执行同一条共享契约导出链路
  - 导出命令：`API_BASE_URL=http://localhost:3250 pnpm openapi-export`

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `chore/public-content-step-17-shared-openapi-contract-sync` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- 说明：`series/public-content -> dev` 不在本 change 内执行，该操作由人工负责
