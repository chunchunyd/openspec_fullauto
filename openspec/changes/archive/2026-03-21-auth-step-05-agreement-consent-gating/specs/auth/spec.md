# Delta for Auth

## ADDED Requirements

### Requirement: 系统必须持久化并判定首次完整登录所需的授权确认状态

系统必须持久化并判定用户对用户协议、隐私政策和 AI 内容告知的必要确认状态，以决定其是否可以进入完整产品能力。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 首次登录后发现缺少必要确认

- WHEN 用户已经通过受控认证流程，但尚未完成必要授权确认
- THEN 系统必须阻止其直接进入完整产品能力

#### Scenario: 完成必要确认后解除阻塞

- WHEN 用户完成必要授权确认并成功写入记录
- THEN 系统必须允许其后续进入完整产品能力
- AND 后续正常登录不得重复阻塞主流程
