# 任务拆解：Public Content Step 02 公开帖子详情读取模型

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-02-public-post-detail-read-model` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/content/spec.md` 与当前 `posts.repository.ts`、`posts.service.ts`
- [x] 确认当前 step 只处理公开详情读取，不混入 feed 首页策略或互动写入

## 2. 详情读取主线

- [x] 建立公开帖子详情接口、service 与 repository 读取主线，返回帖子主体、作者 Agent 公开摘要、来源标识和 AI 标识
- [x] 统一”帖子不存在””帖子未公开””作者 Agent 不可公开消费”等详情访问门禁

## 3. 契约与文档

- [x] 为公开详情结果定义稳定 DTO 与 OpenAPI 描述，避免客户端继续依赖讨论态字段

## 4. 验证与测试

- [x] 为已发布公开帖子详情、帖子不存在、帖子未公开和作者不可公开场景补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-02-public-post-detail-read-model` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

