# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须允许 Agent owner 读取并更新受控的基础资料

系统必须允许 Agent owner 读取并更新受控的基础资料，以支撑后续策略、知识、记忆和公开流程的统一管理入口。 The system MUST allow an agent owner to read and update controlled profile fields through a managed detail boundary.

#### Scenario: owner 读取 Agent 详情

- WHEN 已登录 owner 请求查看自己某个 Agent 的管理详情
- THEN 系统必须返回该 Agent 的受控完整资料结果
- AND 非 owner 不得因为知道 Agent 标识就进入该管理详情

#### Scenario: owner 更新基础资料

- WHEN Agent owner 提交合法的基础资料更新请求
- THEN 系统必须保存允许修改的字段
- AND 不得让该更新越权修改 owner、type 或其他受控系统字段

