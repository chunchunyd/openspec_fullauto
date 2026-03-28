# Delta for Chat

## ADDED Requirements

### Requirement: 系统必须为 owner-scoped private chat 提供受控流式回流与 assistant 消息落地

系统必须为 owner-scoped private chat 提供受控流式回流与 assistant 消息落地，以便聊天回复能够回到正式消息历史主线。 The system MUST provide controlled streaming projection and assistant message persistence for owner-scoped private chat.

#### Scenario: 读取 private chat 回复过程

- WHEN 已登录 owner 读取某次 private chat 回复的流式过程或等价事件结果
- THEN 系统必须返回受控的 chat 语义结果
- AND 不得把 provider 私有事件结构直接作为最终消费接口暴露

#### Scenario: assistant 回复完成并落地

- WHEN 一次 private chat 回复成功完成
- THEN 系统必须将最终 assistant 回复落地为会话历史中的一条消息
- AND 会话的最近消息摘要与最近活跃时间必须随之更新
