# Delta for Feed

## MODIFIED Requirements

### Requirement: 系统必须为公开首页读取提供匿名可读与登录态增强兼容路径

系统必须让公开首页 feed 在保持匿名可读的同时，能够通过可选认证守卫为带合法登录态的调用方返回当前用户相关的最小互动状态，并保持分页输入契约与文档一致。 The system MUST keep the public home-feed path anonymously readable while enriching results for authenticated callers through an optional auth guard and honoring the documented pagination contract.

#### Scenario: 匿名读取公开首页

- WHEN 调用方在不提供认证头的情况下请求公开首页 feed
- THEN 系统必须返回正常的公开首页结果
- AND 不得把该读取路径强制升级为必须登录

#### Scenario: 已登录调用方读取公开首页

- WHEN 调用方带着合法登录态请求公开首页 feed
- THEN 系统必须继续返回同一条公开首页结果主线
- AND 卡片中的最小互动摘要必须能够反映当前用户自己的点赞或收藏状态

#### Scenario: 使用文档允许的分页页长

- WHEN 调用方以查询参数形式传入文档允许范围内的 `limit`
- THEN 系统必须按该页长解释公开首页分页请求
- AND 不得仅因为 HTTP 查询参数以字符串形式传输就将其误判为非法输入

#### Scenario: 可选认证守卫承接公开首页读取

- WHEN 公开首页读取链路通过可选认证守卫识别调用方认证头
- THEN 缺少认证头或认证头不适用公开读取时，系统必须继续允许匿名读取主线
- AND 合法登录态只能增强当前用户相关的最小互动状态，而不得改写公开读取边界
