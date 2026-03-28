# Delta for Admin

## ADDED Requirements

### Requirement: 系统必须对后台用户状态治理动作执行受控权限校验与原因留痕

系统必须对后台用户状态治理动作执行受控权限校验与原因留痕，并将结果写入可追溯的权威审计记录。 The system MUST enforce controlled permissions and reason capture for admin user status governance actions.

#### Scenario: 后台执行用户封禁或解封

- WHEN 具备相应权限的后台用户对某个用户执行封禁或解封
- THEN 系统必须完成受控状态变更或其等价结果
- AND 系统必须记录该动作的操作人、目标对象、原因和结果

#### Scenario: 低权限角色尝试执行高风险治理动作

- WHEN 低权限后台角色尝试执行用户状态治理动作
- THEN 系统必须拒绝该动作
- AND 不得留下未授权但已生效的状态修改
