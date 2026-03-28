# Delta for Interactions

## ADDED Requirements

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

