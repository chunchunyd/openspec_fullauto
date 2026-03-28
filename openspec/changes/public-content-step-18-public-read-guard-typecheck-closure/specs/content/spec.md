# Delta for Content

## MODIFIED Requirements

### Requirement: 系统必须为公开帖子详情返回稳定元数据与可选登录态增强

系统必须让公开帖子详情在保持匿名可读的同时，通过可选认证守卫为带合法登录态的调用方返回与当前用户一致的最小互动状态，并保证详情中的核心时间元数据与真实帖子记录一致。 The system MUST keep public post detail anonymously readable, enrich it with the caller's minimal interaction state through an optional auth guard when authenticated, and preserve truthful detail metadata.

#### Scenario: 匿名读取公开帖子详情

- WHEN 调用方在不提供认证头的情况下读取公开帖子详情
- THEN 系统必须返回该帖子的正常公开详情结果
- AND 不得因为缺少登录态而拒绝其基础公开读取

#### Scenario: 已登录调用方读取公开帖子详情

- WHEN 调用方带着合法登录态读取公开帖子详情
- THEN 系统必须返回该帖子的公开详情结果
- AND 详情中的最小互动摘要必须能够反映当前用户自己的点赞或收藏状态

#### Scenario: 详情返回真实时间元数据

- WHEN 系统返回一条公开帖子详情
- THEN 结果中的创建时间与更新时间必须与底层帖子记录保持一致
- AND 不得用创建时间、占位值或其他替代值冒充真实更新时间

#### Scenario: 可选认证守卫承接公开帖子详情读取

- WHEN 公开帖子详情链路通过可选认证守卫识别调用方认证头
- THEN 缺少认证头或认证头不适用公开详情读取时，系统必须继续允许匿名读取主线
- AND 合法登录态只能增强当前用户相关的最小互动状态，而不得改写详情公开可读边界
