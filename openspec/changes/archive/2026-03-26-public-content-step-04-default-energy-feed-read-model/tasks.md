# 任务拆解：Public Content Step 04 默认能量场读取模型

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-04-default-energy-feed-read-model` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/feed/spec.md`、`openspec/specs/content/spec.md` 与当前 `apps/api` 模块结构
- [x] 确认当前 step 只建立默认首页 feed 读取入口，不混入 Agent 切换或混排策略

## 2. feed 模块与首页入口

- [x] 在 `apps/api` 建立最小 `feed` 模块、controller、service 与 DTO，形成默认能量场读取入口
- [x] 让默认首页 feed 复用 `content` 的公开帖子输出
而不是在 `feed` 内重复写帖子查询真相源

## 3. 默认视角与返回结果

- [x] 明确默认 feed 视角的最小选择规则
并返回首页首屏所需的最小结果结构
- [x] 对空结果和基础错误结果保持受控返回，不把内部依赖细节直接暴露给客户端

## 4. 验证与测试

- [x] 为默认首页 feed 读取、空结果与依赖 `content` 输出的集成边界补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件
测试文件头注释需要写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-04-default-energy-feed-read-model` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

