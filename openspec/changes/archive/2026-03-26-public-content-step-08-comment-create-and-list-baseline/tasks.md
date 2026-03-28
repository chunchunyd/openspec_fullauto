# 任务拆解：Public Content Step 08 评论创建与列表基线

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-08-comment-create-and-list-baseline` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/interactions/spec.md`、`openspec/specs/content/spec.md` 与公开帖子详情主线
- [x] 确认当前 step 只建立评论创建与列表，不混入评论点赞、多级楼中楼或审核结论

## 2. 数据模型与写入边界

- [x] 为评论补齐最小持久化锚点、帖子关联、作者类型标识和可见性边界
- [x] 限定评论创建只作用于当前允许评论的公开帖子

## 3. 接口与读取主线

- [x] 建立发表评论接口与按帖子读取评论列表接口
- [x] 返回评论作者最小摘要和作者类型，避免客户端自行猜测评论主体身份

## 4. 验证与测试

- [x] 为评论创建成功、不可评论帖子拒绝、评论列表读取和作者类型返回补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-08-comment-create-and-list-baseline` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

