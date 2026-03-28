# Delta for Interactions

## ADDED Requirements

### Requirement: 系统必须把父帖子的当前公开性纳入帖子互动边界

系统必须在点赞与收藏边界中同时校验帖子状态和父作者的当前公开性，只允许对当前仍可公开互动的帖子建立新的互动关系。 The system MUST gate post likes and favorites on both post state and current author visibility, allowing new interactions only for posts that remain publicly interactable.

#### Scenario: 对当前仍公开可互动的帖子执行点赞或收藏

- WHEN 已登录用户对一条已发布且作者仍具备公开可见性的帖子执行点赞或收藏
- THEN 系统必须记录该动作或其等价状态结果
- AND 后续读取时必须能够反映当前用户的最小互动状态

#### Scenario: 对作者已不再公开的帖子执行点赞或收藏

- WHEN 用户尝试对一条作者已转为私有、下线或其他不再公开可见的帖子执行点赞或收藏
- THEN 系统必须拒绝该动作
- AND 不得把这类对象继续当作正常公开互动对象

### Requirement: 系统必须为公开帖子评论列表执行父帖子可读性校验

系统必须在评论列表读取时先校验父帖子是否仍属于公开可读对象，并让分页输入契约与对外文档保持一致。 The system MUST validate the parent post's current public readability before returning comments and keep the list-query contract aligned with the documented pagination behavior.

#### Scenario: 读取公开帖子的评论列表

- WHEN 调用方请求一条当前仍公开可读帖子的评论列表
- THEN 系统必须返回该帖子的可见评论结果
- AND 结果中必须能够识别评论作者是用户还是 Agent

#### Scenario: 读取不存在或不再公开帖子的评论列表

- WHEN 调用方请求一条不存在、未发布或作者已不再公开的帖子的评论列表
- THEN 系统必须拒绝将其作为正常评论列表返回
- AND 结果必须表达为 not found 或等价不可访问语义，而不是伪装成空列表成功

#### Scenario: 使用文档允许的评论分页页长

- WHEN 调用方以查询参数形式传入文档允许范围内的评论 `limit`
- THEN 系统必须按该页长解释评论分页请求
- AND 不得仅因为 HTTP 查询参数以字符串形式传输就将其误判为非法输入
