# Delta for Admin

## ADDED Requirements

### Requirement: 系统必须以受控状态机执行用户封禁与解封

系统必须以受控状态机执行用户封禁与解封，并保留恢复封禁前状态所需的最小依据，而不是在解封时默认覆盖其他业务主状态。 The system MUST perform admin user ban and unban through a controlled state machine that can restore the pre-ban state without overwriting unrelated lifecycle ownership.

#### Scenario: 解封恢复封禁前状态

- WHEN 一个具备权限的后台用户解封先前已封禁的用户
- THEN 系统必须恢复到该用户受支持的封禁前状态或其等价结果
- AND 不得默认把所有已封禁用户都写回 `ACTIVE`

#### Scenario: 缺少恢复依据时的受控失败

- WHEN 系统需要解封一个缺少恢复依据或命中非法状态转换的已封禁用户
- THEN 系统必须返回受控失败结果
- AND 不得通过静默回写制造新的错误主状态

