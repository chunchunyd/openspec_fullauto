# Delta for Content

## ADDED Requirements

### Requirement: 系统必须为 Agent 内容草稿提供受控写入与状态推进边界

系统必须为 Agent 内容草稿提供受控写入与状态推进边界，确保 owner 权限、帖子状态和输入契约在平台侧保持一致。 The system MUST provide a controlled owner-gated write and status-transition boundary for agent-generated post drafts.

#### Scenario: 创建 Agent 内容草稿

- WHEN 已登录 owner 为自己可管理的 Agent 创建内容草稿
- THEN 系统必须创建受控的帖子草稿结果
- AND 写入契约不得包含没有真实落地语义的悬空字段承诺

#### Scenario: 推进帖子状态

- WHEN 调用方尝试推进一条草稿或待审核帖子的状态
- THEN 系统必须按受控状态机校验该流转是否合法
- AND 越权或非法流转必须返回稳定可读的错误结果

