# Delta for Chat

## MODIFIED Requirements

### Requirement: 系统必须在轮询主线中恢复遗漏的 finalize 与 assistant 消息回填

系统必须让 chat polling 主线在 task 已完成但 finalize 尚未完全收口时，能够恢复 assistant 消息、触发用户消息状态和会话读模型，而不是仅以 assistant 消息是否已存在作为 finalize 已完成的判断。 The system MUST recover missed polling finalization by reconciling the assistant message, triggering user-message status, and conversation read model as one controlled completion path.

#### Scenario: finalize 首次失败后再次轮询

- **WHEN** 某次 polling 已经判断 task 完成，但上一次 finalize 或消息落地失败
- **THEN** 后续再次轮询时系统必须能够进入受控恢复路径并再次尝试补齐 assistant 消息或剩余读模型状态
- **AND** 不得因为之前已经错过完成事件而永久放弃 finalize

#### Scenario: 客户端越过完成事件后恢复轮询

- **WHEN** 客户端恢复轮询时，`afterSeq` 已经越过最初的完成事件所在页，但 task 实际已经完成
- **THEN** 系统必须仍然能够识别“task 已完成但 finalize 未全部收口”的状态
- **AND** 必须把 assistant 消息和相关读模型补回正式历史主线，而不是只返回一个没有消息落地或读模型修复的完成标记

#### Scenario: assistant 消息已存在但读模型未收口

- **WHEN** 某次历史失败已经创建了 assistant 消息，但触发用户消息状态仍未进入完成态，或会话最近活跃时间/摘要仍未对齐最终回复
- **THEN** 系统必须继续执行剩余 reconcile，而不是仅因 assistant 消息存在就视为 finalize 已完成
- **AND** 重复恢复不得重复生成新的 assistant 消息
