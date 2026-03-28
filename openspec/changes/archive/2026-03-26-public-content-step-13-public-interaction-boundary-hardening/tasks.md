# 任务拆解：Public Content Step 13 公开互动边界加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `fix/public-content-step-13-public-interaction-boundary-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [x] 在进入 `fix/public-content-step-13-public-interaction-boundary-hardening` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [x] 如果是续跑或接手已有 worktree，先检查当前实现分支上的 staged / unstaged / untracked 改动，并将其作为继承现场处理
- [x] 确认当前 step 只收口公开互动对象边界与对应回归护栏，不混入 public feed/detail 读侧增强或新的互动能力扩张
- [x] 阅读 `reports/api/public-content/app-api-public-content-review-v1.md`、`public-content` step-07 / 08 / 11 归档结果、当前 `posts.repository.ts` 公开帖子查询边界，以及当前 interactions service 测试失败现场，确认复用点和缺口

## 2. 公开互动对象边界加固

- [x] 收紧 post like / favorite 的公开互动判断，确保帖子状态与作者公开性共同决定是否允许建立新互动
- [x] 收紧 comments list 的父帖子公开可读校验，并对不存在 / 未公开父帖子返回稳定 404，而不是 `200 + []`
- [x] 对齐 comments list `limit` 查询参数的数字转换与分页校验，避免文档可用但真实请求 400

## 3. 回归护栏恢复

- [x] 修复 follows / comments / reports service 测试对 `BehaviorSignalService` 的 provider / mock 缺口，并为代表性成功路径补齐行为信号断言
- [x] 为未发布帖子、作者不公开帖子、缺失帖子与正常公开帖子场景补齐 interactions 边界回归测试
- [x] 如果本 step 影响 `packages/api_contracts/openapi/openapi.json`，同步更新相关契约产物并核对 comments / likes / favorites 代表性接口说明（本 step 不影响 openapi 契约）

## 4. 验证与测试

- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 按验收问题对应链路执行 interactions 相关单测或等价验证，确认 service 回归护栏恢复为绿色
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本 step 的有效改动，并在交接前确认实现分支工作区干净
- [x] 自动化将 `fix/public-content-step-13-public-interaction-boundary-hardening` merge 回 `series/public-content`，保留实现分支上的阶段性提交历史
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围
