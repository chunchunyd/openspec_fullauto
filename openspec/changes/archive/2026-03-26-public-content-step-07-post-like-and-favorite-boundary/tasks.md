# 任务拆解：Public Content Step 07 帖子点赞与收藏边界

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-07-post-like-and-favorite-boundary` 实现分支，  并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/interactions/spec.md`、`openspec/specs/content/spec.md` 与当前公开帖子读取主线
- [x] 确认当前 step 只建立点赞与收藏边界
  不混入评论、关注、举报或互动摘要投影

## 2. 数据模型与写入边界

- [x] 为帖子点赞与收藏补齐最小持久化锚点、幂等约束和取消操作语义
  - Added `PostLike` and `PostFavorite` models to schema.prisma
  - Implemented soft-delete pattern with `unlikedAt`/`unfavoritedAt` timestamps
  - Unique constraints on `(userId, postId)` for idempotency
- [x] 限定这些动作只作用于当前允许公开互动的帖子
  不把对象状态校验下推给客户端
  - Service layer enforces `PUBLISHED` status check before allowing interactions
  - Returns `POST_NOT_INTERACTABLE` error for non-published posts

## 3. 接口与读取结果

- [x] 建立点赞与收藏的最小接口，返回当前用户动作后的受控结果
  - POST `/interactions/posts/:postId/like` - Like a post (idempotent)
  - DELETE `/interactions/posts/:postId/like` - Unlike a post (idempotent)
  - GET `/interactions/posts/:postId/like/status` - Get like status
  - POST `/interactions/posts/:postId/favorite` - Favorite a post (idempotent)
  - DELETE `/interactions/posts/:postId/favorite` - Unfavorite a post (idempotent)
  - GET `/interactions/posts/:postId/favorite/status` - Get favorite status
- [x] 为后续详情和摘要读取保留最小状态读取出口
  - `getLikeStatus()` and `getFavoriteStatus()` methods in services
  - `isLiked()` and `isFavorited()` convenience methods
  - `batchGetLikeStatus()` and `batchGetFavoriteStatus()` for batch queries

## 4. 验证与测试

- [x] 为点赞、取消点赞、收藏、取消收藏、不可互动对象拒绝与重复操作幂等补充测试
  - Added `post-likes.service.spec.ts` with comprehensive test coverage
  - Added `post-favorites.service.spec.ts` with comprehensive test coverage
  - Tests cover: success cases, idempotency, boundary rejections
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收
  确认本 step 不引入新的风格问题
  - ESLint validation passed with no errors
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收
  确认本 step 不引入新的类型错误
  - TypeScript validation passed with no errors
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令
  - All test files include execution command in header comments

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-07-post-like-and-favorite-boundary` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围
