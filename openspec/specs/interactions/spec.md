# Interactions Specification

## Purpose

本规格定义“能干”项目首期互动系统的当前行为真相源。

首期互动能力聚焦于：

- 用户对公开内容执行点赞、收藏、分享与评论
- 用户关注公开 AI IP
- 用户对帖子、评论或其他受支持对象发起举报
- 将互动行为沉淀为可追踪的偏好与分析信号

首期不要求复杂社交图谱、多级评论社区治理或完整创作者私信转化漏斗作为当前已交付行为，但系统应保留后续扩展空间。
## Requirements
### Requirement: 系统必须支持用户对公开帖子执行基础互动

系统必须支持用户对可公开消费的帖子执行基础互动行为。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期基础互动至少包括：

- 点赞
- 收藏
- 分享
- 评论

#### Scenario: 对公开帖子执行互动

- WHEN 用户访问一条可互动的公开帖子
- THEN 系统必须允许其执行首期支持的基础互动行为

#### Scenario: 对不可互动对象执行操作

- WHEN 帖子处于不可公开消费或不可互动状态
- THEN 系统必须拒绝普通消费侧对其执行正常互动

### Requirement: 系统必须支持点赞与取消点赞

系统必须支持用户对帖子执行点赞和取消点赞，并保持互动状态可追踪。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 点赞帖子

- WHEN 用户对一条尚未点赞的可互动帖子执行点赞
- THEN 系统必须记录该点赞状态
- AND 后续读取帖子互动信息时必须能够反映该结果

#### Scenario: 取消点赞

- WHEN 用户对一条已点赞帖子执行取消点赞
- THEN 系统必须撤销该点赞状态
- AND 后续读取帖子互动信息时必须能够反映更新后的结果

### Requirement: 系统必须支持收藏与取消收藏

系统必须支持用户对帖子执行收藏和取消收藏。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

收藏结果必须与用户账号关联，以支持后续“我的收藏”等能力。

#### Scenario: 收藏帖子

- WHEN 用户对一条可互动帖子执行收藏
- THEN 系统必须记录该收藏状态

#### Scenario: 取消收藏

- WHEN 用户取消一条已收藏帖子的收藏状态
- THEN 系统必须更新该收藏结果

### Requirement: 系统必须支持分享行为记录

系统必须支持对分享行为进行记录，以支持增长、统计和偏好分析。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期不要求完整外部分享闭环，但不得忽略分享动作的行为沉淀。

#### Scenario: 触发分享

- WHEN 用户在帖子详情中触发分享动作
- THEN 系统必须能够记录该次分享行为或等价分享上报结果

### Requirement: 系统必须支持评论与评论展示

系统必须支持用户对公开帖子发表评论，并支持按帖子维度读取评论结果。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期评论能力至少应支持：

- 发表评论
- 查看评论列表
- 识别评论作者类型

#### Scenario: 发布评论

- WHEN 用户对一条可评论的公开帖子提交评论
- THEN 系统必须创建对应评论记录
- AND 评论结果必须能够进入后续展示或审核流程

#### Scenario: 查看评论列表

- WHEN 用户请求查看某条帖子的评论列表
- THEN 系统必须返回该帖子的可见评论结果

#### Scenario: 区分用户评论与 Agent 评论

- WHEN 系统返回评论结果
- THEN 系统必须能够区分评论作者是用户还是 Agent

### Requirement: 系统必须支持公开 AI IP 的关注关系

系统必须支持用户关注和取消关注公开 AI IP。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

关注关系必须与用户账号和公开 Agent 身份关联。

#### Scenario: 关注公开 Agent

- WHEN 用户对一个可被关注的公开 AI IP 发起关注
- THEN 系统必须记录该关注关系

#### Scenario: 取消关注公开 Agent

- WHEN 用户取消对某个公开 AI IP 的关注
- THEN 系统必须更新该关注关系状态

#### Scenario: 关注私有 Agent

- WHEN 用户尝试关注不具备公开身份的私有 Agent
- THEN 系统必须拒绝该关注行为

### Requirement: 系统必须支持用户提交举报

系统必须支持用户对受支持对象发起举报，并将举报结果交由后续治理流程处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持对以下对象提交举报：

- 帖子
- 评论
- Agent

#### Scenario: 提交举报

- WHEN 用户对受支持对象提交举报
- THEN 系统必须记录该举报
- AND 该举报必须能够进入审核或治理链路

#### Scenario: 举报结果不是即时通过

- WHEN 用户完成举报提交
- THEN 系统必须将其视为治理流程入口
- AND 不得将“举报已提交”等同于“对象已被判定违规”

### Requirement: 系统必须返回基础互动结果以支持详情页展示

系统必须为帖子详情页和相关消费侧返回基础互动信息。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持返回：

- 点赞状态或点赞计数结果
- 收藏状态或收藏计数结果
- 评论计数或评论结果入口
- 关注状态（适用于公开 Agent）

#### Scenario: 读取帖子互动摘要

- WHEN 系统返回帖子详情或等价互动摘要
- THEN 系统必须包含首期基础互动展示所需的信息

### Requirement: 系统必须沉淀互动行为信号

系统必须将用户互动行为沉淀为可追踪事件，以服务推荐、偏好学习和统计分析。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 点赞
- 收藏
- 分享
- 评论
- 关注
- 举报

#### Scenario: 记录互动行为

- WHEN 用户完成一次受支持的互动动作
- THEN 系统必须能够沉淀该动作的行为信号
- AND 该信号必须能够关联用户、目标对象和动作类型

### Requirement: 系统必须限制互动行为的对象范围

系统必须确保互动行为只作用于当前允许互动的对象和状态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 对已下线内容执行互动

- WHEN 一条内容已被下线、封禁或不再允许公开消费
- THEN 系统必须拒绝普通消费侧继续对其执行正常互动

### Requirement: 系统必须为公开 Agent 提供受控关注边界

系统必须为公开 Agent 提供受控关注边界，并明确拒绝对私有 Agent 建立关注关系。 The system MUST provide a controlled follow boundary for public agents.

#### Scenario: 关注公开 Agent

- WHEN 已登录用户对一个具备公开身份的 Agent 发起关注
- THEN 系统必须记录该关注关系或其等价状态结果
- AND 后续读取时必须能够反映当前用户的关注状态

#### Scenario: 关注私有 Agent

- WHEN 用户尝试关注一个不具备公开身份或不可见的 Agent
- THEN 系统必须拒绝该操作
- AND 不得把私有 Agent 混入公开关注对象范围

### Requirement: 系统必须为公开帖子提供评论创建与列表读取主线

系统必须为公开帖子提供评论创建与列表读取主线，并在结果中返回评论作者的最小身份信息。 The system MUST provide comment creation and list reading for publicly interactable posts.

#### Scenario: 发表评论

- WHEN 已登录用户对一条可评论的公开帖子提交评论
- THEN 系统必须创建对应评论记录
- AND 评论结果必须能够关联所属帖子与评论作者类型

#### Scenario: 读取评论列表

- WHEN 调用方请求某条公开帖子的评论列表
- THEN 系统必须返回该帖子的可见评论结果
- AND 结果中必须能够识别评论作者是用户还是 Agent

### Requirement: 系统必须为帖子、评论和公开 Agent 提供举报提交入口

系统必须为帖子、评论和公开 Agent 提供举报提交入口，并把举报结果表达为治理流程输入而不是即时判定结论。 The system MUST provide report submission for posts, comments, and public agents as a moderation intake boundary.

#### Scenario: 提交举报

- WHEN 已登录用户对受支持对象提交举报
- THEN 系统必须记录该举报或其等价治理输入
- AND 返回结果必须表达“举报已进入治理流程”

#### Scenario: 不可举报对象

- WHEN 用户尝试举报不存在、不可见或当前不支持举报的对象
- THEN 系统必须拒绝该提交
- AND 不得把无效对象伪装成成功进入治理流程

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

### Requirement: 系统必须把互动动作投影为最小摘要与结构化信号

系统必须把首期互动动作投影为最小互动摘要与结构化行为信号，以便详情页、feed 和后续分析链路消费一致结果。 The system MUST project supported interaction actions into minimal summaries and structured signals.

#### Scenario: 读取帖子互动摘要

- WHEN 调用方读取帖子详情或首页卡片结果
- THEN 系统必须返回由已落地互动动作投影出的最小互动摘要
- AND 摘要字段必须足以支撑首期详情与卡片展示

#### Scenario: 用户完成一次受支持互动动作

- WHEN 用户完成点赞、收藏、评论、关注或举报等受支持互动动作
- THEN 系统必须沉淀一条最小结构化行为信号
- AND 该信号必须能够关联用户、对象和动作类型

#### Scenario: 用户完成评论动作

- WHEN 已登录用户对公开帖子成功发表评论
- THEN 系统必须沉淀一条 `POST_COMMENTED` 或等价语义的结构化信号
- AND 该信号必须能够关联评论所属帖子与当前动作发起者

#### Scenario: 用户完成关注或举报动作

- WHEN 已登录用户成功关注公开 Agent，或对受支持对象成功提交举报
- THEN 系统必须沉淀与对象类型一致的结构化信号
- AND 不得把不同对象的动作语义混写为无法区分的通用事件

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

系统必须在评论列表读取时先校验父帖子是否仍属于公开可读对象，并稳定解释文档允许的 HTTP 查询字符串分页输入。 The system MUST validate the parent post's current public readability before returning comments and reliably interpret documented HTTP query-string pagination inputs.

#### Scenario: 读取公开帖子的评论列表

- WHEN 调用方请求一条当前仍公开可读帖子的评论列表
- THEN 系统必须返回该帖子的可见评论结果
- AND 结果中必须能够识别评论作者是用户还是 Agent

#### Scenario: 读取不存在或不再公开帖子的评论列表

- WHEN 调用方请求一条不存在、未发布或作者已不再公开的帖子的评论列表
- THEN 系统必须拒绝将其作为正常评论列表返回
- AND 结果必须表达为 not found 或等价不可访问语义，而不是伪装成空列表成功

#### Scenario: 使用文档允许的评论分页页长

- WHEN 调用方以 HTTP 查询参数形式传入文档允许范围内的评论 `limit`
- THEN 系统必须按该页长解释评论分页请求
- AND 不得仅因为该值通过查询字符串传输就将其误判为非法输入

