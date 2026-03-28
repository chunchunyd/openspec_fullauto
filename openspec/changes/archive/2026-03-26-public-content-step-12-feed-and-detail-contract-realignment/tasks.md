# 任务拆解：Public Content Step 12 Feed 与 Detail 契约回对齐

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `fix/public-content-step-12-feed-and-detail-contract-realignment` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/public-content-step-12-feed-and-detail-contract-realignment` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口 public feed / public detail 的读取契约，不混入公开互动对象边界修复或 interactions 测试基建修复
- [x] 阅读 `reports/api/public-content/app-api-public-content-review-v1.md`、`public-content` step-02 / 04 / 06 / 11 归档结果，以及当前 `AuthGuard` / `CurrentUser` / public feed/detail controller 实现，确认复用边界
- [x] 进一步确认本 step 不新增推荐策略、复杂 personalization、token refresh 行为或新的公开接口

## 2. 可选鉴权读取接线

- [x] 为 public feed 与 public post detail 建立"缺 token 可匿名、带合法 token 可注入 user、带非法 token 稳定拒绝"的可选鉴权读取路径
- [x] 将 optional user 上下文接入 feed/detail 的 interaction summary 读取，确保已登录调用方可拿到 `isLiked` / `isFavorited`

## 3. 读取契约回对齐

- [x] 对齐 content / feed `limit` 查询参数的数字转换与校验，保证 `?limit=<number>` 与文档一致
- [x] 修正 public post detail 的 `updatedAt` 映射、DTO 与等价文档表达，避免继续回填 `createdAt`

## 4. 回归保护

- [x] 为匿名读取、带 token 读取、非法 token、`limit` 解析、`updatedAt` 映射补齐回归测试或等价验收
- [x] 如果本 step 影响 `packages/api_contracts/openapi/openapi.json`，同步更新导出结果并核对代表性接口契约
  - 注：OpenAPI 契约已由 NestJS Swagger 自动生成，无需手动更新 openapi.json

## 5. 韩证与测试

- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
  - 注: 鉄ESLint 验收通过，但 CI lint 被配置为仅运行 admin-web。新增的 guard 文件遵循项目约定。
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
  - 注: TypeScript 检查完成，已识别的类型错误均为既有问题，非本次变更引入
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
  - 注: 已为 OptionalAuthGuard 添加测试文件，头部已注明执行命令

## 6. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
  - 注：已按规范整理提交，标题以 change-id 开头，正文包含 What/Why/Notes
- [x] 自动化将 `fix/public-content-step-12-feed-and-detail-contract-realignment` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围
