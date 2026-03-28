# Delta for Chat

## MODIFIED Requirements

### Requirement: 系统必须在轮询主线中恢复遗漏的 finalize 与 assistant 消息回填

系统必须让 chat polling 主线在 task 已完成但 finalize 尚未完全收口时，能够把 assistant 消息、触发用户消息状态、会话最近活跃时间或等价排序读模型，以及平台 task 最终成功态一起收口，而不是只检查其中单个标志位。 The system MUST reconcile the full finalize target state, including assistant persistence, user-message completion, conversation read-model alignment, and platform task success state, before treating polling finalization as complete.

#### Scenario: finalize 首次失败后再次轮询

- **WHEN** 某次 polling 已经判断 task 完成，但上一次 finalize 或消息落地失败
- **THEN** 后续再次轮询时系统必须能够进入受控恢复路径并再次尝试补齐 assistant 消息或剩余读模型状态
- **AND** 不得因为之前已经错过完成事件而永久放弃 finalize

#### Scenario: 客户端越过完成事件后恢复轮询

- **WHEN** 客户端恢复轮询时，`afterSeq` 已经越过最初的完成事件所在页，但 task 实际已经完成
- **THEN** 系统必须仍然能够识别“task 已完成但 finalize 未全部收口”的状态
- **AND** 必须把 assistant 消息和相关读模型补回正式历史主线，而不是只返回一个没有消息落地或读模型修复的完成标记

#### Scenario: assistant 消息已存在但目标态仍有缺口

- **WHEN** 某次历史失败已经创建了 assistant 消息，且 user message 可能已经完成，但 conversation 最近活跃时间、等价排序读模型或平台 task 成功态仍未对齐
- **THEN** 系统必须继续执行剩余 reconcile，而不是仅因部分目标态已达成就视为 finalize 已完成
- **AND** 重复恢复不得重复生成新的 assistant 消息

#### Scenario: 重复 finalize 只在完整目标态成立时早退

- **WHEN** duplicate finalize 或重复 polling 命中同一条已存在的 assistant 消息
- **THEN** 系统只有在 assistant、user message、conversation 读模型和平台 task 成功态均已达成时才允许 early return
- **AND** 任何剩余缺口都必须继续进入幂等补偿路径
