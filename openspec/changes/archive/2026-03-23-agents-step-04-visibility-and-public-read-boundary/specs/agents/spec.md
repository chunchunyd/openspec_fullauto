# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须对 Agent 管理读取与 public read 施加不同访问边界

系统必须对 Agent 管理读取与 public read 施加不同访问边界，以避免 private 管理数据被普通消费侧误读。 The system MUST enforce distinct access boundaries for owner-managed agent reads and public agent reads.

#### Scenario: 非 owner 读取 private Agent

- WHEN 非 owner 尝试读取一个不具备公开访问条件的 Agent
- THEN 系统必须拒绝该读取
- AND 不得返回该 Agent 的管理详情或等价私有结果

#### Scenario: 读取公开可见 Agent

- WHEN 普通消费侧读取一个已经满足公开访问条件的 Agent
- THEN 系统必须返回受控的 public read 结果
- AND 返回字段不得混入仅供 owner 管理使用的内部信息

