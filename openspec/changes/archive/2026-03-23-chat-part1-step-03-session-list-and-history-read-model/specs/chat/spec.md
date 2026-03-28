# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须为 owner-scoped private chat 返回最小会话列表与历史读取结果

系统必须为 owner-scoped private chat 返回最小会话列表与历史读取结果，以支撑培养皿首页与单聊页的正式读取主线。 The system MUST return a minimal read model for owner-scoped private chat session lists and message history.

#### Scenario: 查看 private chat 会话列表

- WHEN 已登录 owner 进入培养皿首页
- THEN 系统必须返回该用户可管理的 private chat 会话列表
- AND 列表结果必须包含最近消息摘要与最近活跃时间

#### Scenario: 分页读取 private chat 历史消息

- WHEN 已登录 owner 请求某个 private chat 会话的历史消息
- THEN 系统必须按稳定顺序返回该会话的消息分页结果
- AND 不得允许调用方通过会话标识越权读取他人的 private chat 历史
