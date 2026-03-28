# 任务拆解：Public Content Step 11 互动信号与摘要投影

## 1. 实施前门禁

- [x] 自动化确认系列集成分支 `series/public-content` 已就绪（若不存在则从最新 `dev` 创建）
- [x] 自动化从 `series/public-content` 切出 `feat/public-content-step-11-interaction-signal-and-summary-projection` 实现分支，并将当前 worktree 绑定到该分支
- [x] 阅读现有 `openspec/specs/interactions/spec.md`、`openspec/specs/feed/spec.md`、`openspec/specs/content/spec.md` 与当前互动写入主线
- [x] 确认当前 step 只补互动摘要与最小信号沉淀，不扩展成完整分析平台或复杂推荐系统

## 2. 共享信号与摘要依赖检查

- [x] 检查现有 `packages/event_schema`、analytics 相关共享契约或等价结构是否可复用；若当前阶段不足以支撑完整共享导出，则先在本 step 明确最小可追踪信号边界
- [x] 明确互动摘要由哪些动作投影而来，以及详情页与 feed 卡片分别消费哪些最小字段

## 3. 摘要投影与结果接线

- [x] Feed 模块互动摘要集成（已完成：InteractionSummaryService、DTOs、FeedService/Controller 集成）
- [x] Content 模块 Post Detail 互动摘要集成（已完成：为帖子详情页添加互动摘要）
- [x] 将已落地的互动动作沉淀为最小结构化行为信号，保证后续推荐或统计可以继续消费

## 4. 验证与测试

- [x] 为互动摘要投影、详情与首页结果接线、结构化行为信号写入补充测试
- [x] 按 `docs/eslint-style-notes.md` 中的当前约定执行 ESLint 验收，确认本 step 不引入新的风格问题
- [x] 按 `docs/tsc-fix-summary.md` 中的当前约定执行 TypeScript 验收，确认本 step 不引入新的类型错误
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

## 5. 合并与收口

- [x] 自动化将 `feat/public-content-step-11-interaction-signal-and-summary-projection` squash merge 回 `series/public-content`
- `series/public-content -> dev` 的最终回合并由人工负责，不纳入本 change 的执行范围

## 实施笔记

### 已完成工作

1. **InteractionSummaryService** (`apps/api/src/modules/interactions/interaction-summary.service.ts`)
   - 创建互动摘要聚合服务
   - 支持批量查询优化（避免 N+1 问题）
   - 为登录用户提供 isLiked/isFavorited 状态
   - 提供 getBatchInteractionSummary 和 getFeedCardInteractionSummary 方法

2. **Interaction Summary DTOs** (`apps/api/src/modules/interactions/dto/interaction-summary.dto.ts`)
   - 定义 PostInteractionSummaryDto、FeedCardInteractionSummaryDto
   - 定义 BatchInteractionSummaryResult、InteractionSummaryQueryOptions
   - 定义 PostInteractionSummaryWithStatusDto

3. **Feed 模块集成**（已完成）
   - FeedModule 导入 InteractionsModule
   - FeedService 注入 InteractionSummaryService
   - FeedController 映射 interaction 字段到 FeedCardDto
   - feed.dto.ts 添加 FeedCardInteractionSummaryDto
   - FeedCardDto 包含 interaction 字段

4. **Content 模块集成**（已完成）
   - ContentModule 导入 InteractionsModule（使用 forwardRef 解决循环依赖）
   - ContentController 注入 InteractionSummaryService
   - 为帖子详情页添加互动摘要
   - posts.dto.ts 添加 PostDetailInteractionSummaryDto

5. **BehaviorSignalService** (`apps/api/src/modules/interactions/behavior-signal.service.ts`)
   - 创建行为信号发射服务
   - 定义 BehaviorSignalAction 枚举（POST_LIKED, POST_FAVORITED, POST_COMMENTED, AGENT_FOLLOWED 等）
   - 定义 BehaviorSignalTargetType 枚举（POST, COMMENT, AGENT）
   - 提供 emit、emitPostSignal、emitAgentSignal、emitCommentSignal 方法
   - 当前实现为日志输出，预留接口供后续扩展

6. **行为信号集成**（已完成）
   - PostLikesService: POST_LIKED, POST_UNLIKED 信号
   - PostFavoritesService: POST_FAVORITED, POST_UNFAVORITED 信号
   - FollowsService: AGENT_FOLLOWED, AGENT_UNFOLLOWED 信号
   - CommentsService: POST_COMMENTED 信号
   - ReportsService: POST_REPORTED, COMMENT_REPORTED, AGENT_REPORTED 信号

7. **测试文件**（已完成）
   - InteractionSummaryService 单元测试
   - BehaviorSignalService 单元测试
   - 测试文件头注释写明完整执行命令

### 预存问题

- Prisma client 未生成导致的类型错误（非本 step 引入）
