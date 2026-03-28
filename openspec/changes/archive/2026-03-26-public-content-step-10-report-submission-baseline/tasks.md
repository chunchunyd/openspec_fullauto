# 任务拆解：Public Content Step 10 举报提交基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-10-report-submission-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/interactions/spec.md`、`openspec/specs/moderation/spec.md` 与当前公开帖子/评论主线
- [x] 确认当前 step 只建立举报提交入口，不混入审核判定与管理端处置

## 2. 举报数据模型与对象范围

- [x] 为帖子、评论和公开 Agent 的举报提交补齐最小持久化锚点与对象类型约束
- [x] 明确"可举报对象存在但尚未判定"和"对象不存在或不可举报"的差异化校验

## 3. 提交接口与结果语义

- [x] 建立举报提交接口，返回"已提交治理入口"的受控结果
- [x] 在契约中明确举报提交不等于即时违规判定

## 4. 验证与测试

- [x] 为帖子举报、评论举报、Agent 举报、不可举报对象拒绝和重复提交边界补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-10-report-submission-baseline` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围
