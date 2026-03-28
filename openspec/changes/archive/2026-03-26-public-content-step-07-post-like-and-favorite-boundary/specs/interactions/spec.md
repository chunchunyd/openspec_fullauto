# Delta for Interactions

## ADDED Requirements

### Requirement: 系统必须为公开帖子提供受控的点赞与收藏边界

系统必须为公开帖子提供受控的点赞与收藏边界，只允许对当前可公开互动的帖子执行这些动作。 The system MUST provide controlled like and favorite boundaries for publicly interactable posts.

#### Scenario: 对公开帖子执行点赞或收藏

- WHEN 已登录用户对一条可公开互动的帖子执行点赞或收藏
- THEN 系统必须记录该动作或其等价状态结果
- AND 后续读取时必须能够反映当前用户的最小互动状态

#### Scenario: 对不可互动帖子执行操作

- WHEN 用户尝试对未公开、已下线或不允许互动的帖子执行点赞或收藏
- THEN 系统必须拒绝该动作
- AND 不得把对象状态判断责任交给客户端硬编码

