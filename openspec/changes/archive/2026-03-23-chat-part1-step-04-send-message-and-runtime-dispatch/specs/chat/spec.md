# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须把 owner-scoped private chat 文本发送映射为受控 runtime 调用

系统必须把 owner-scoped private chat 文本发送映射为受控 runtime 调用，以避免 `chat` 只停留在只读历史页而没有正式协作入口。 The system MUST map owner-scoped private chat text sends to a controlled runtime dispatch.

#### Scenario: 发送 private chat 文本消息

- WHEN 已登录 owner 向自己可管理的 private Agent 发送一条合法文本消息
- THEN 系统必须持久化该用户消息并创建或关联统一 Agent task
- AND 平台必须通过共享 runtime provider 发起对应 dispatch

#### Scenario: 无权限或非法输入的发送请求

- WHEN 用户尝试向不具备 owner 访问条件的 Agent 发送消息，或提交空内容/非法内容
- THEN 系统必须在进入 runtime 前拒绝该请求
- AND `chat` 不得把这类业务校验责任下推给 runtime
