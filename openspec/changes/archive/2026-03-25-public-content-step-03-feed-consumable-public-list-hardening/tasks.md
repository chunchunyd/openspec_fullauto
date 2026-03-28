# 任务拆解：Public Content Step 03 Feed 可消费公开列表加固

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-03-feed-consumable-public-list-hardening` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/content/spec.md` 与当前公开列表实现
- [x] 确认当前 step 只加固公开列表输出，不混入 feed 首页聚合、切换或互动逻辑

## 2. 公开列表输出加固

- [x] 收紧公开帖子列表的过滤条件、排序规则和游标语义，确保分页结果稳定可追踪
- [x] 固化 feed 卡片最小字段集合，明确哪些字段由 `content` 提供，哪些策略字段留给 `feed`

## 3. 契约与职责边界

- [x] 在 DTO 与 OpenAPI 中明确该接口只输出可公开消费帖子，不承担首页混排、推荐或互动聚合职责

## 4. 验证与测试

- [x] 为公开过滤、稳定分页、空页结果和卡片字段映射补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-03-feed-consumable-public-list-hardening` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

