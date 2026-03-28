# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须为 owner-scoped private Agent 单聊持久化受控会话与消息锚点

系统必须为 owner-scoped private Agent 单聊持久化受控会话与消息锚点，以避免培养皿列表、历史消息、任务关联和回复投影长期依赖内存态或 runtime 私有状态。 The system MUST persist controlled conversation and message anchors for owner-scoped private agent chats.

#### Scenario: 首次与私有 Agent 建立单聊锚点

- WHEN 已登录用户首次与自己可管理的 private Agent 发起单聊
- THEN 系统必须能够创建或获得该用户与该 Agent 的受控会话锚点
- AND 后续同一 owner 与同一 Agent 的主单聊不得无约束地产生重复平行会话

#### Scenario: 持久化用户消息与 assistant 消息落点

- WHEN 单聊链路创建一条用户消息或后续 assistant 消息
- THEN 系统必须能够把该消息持久化到受控消息锚点
- AND 消息记录必须能够关联所属会话与基础发送方类型
