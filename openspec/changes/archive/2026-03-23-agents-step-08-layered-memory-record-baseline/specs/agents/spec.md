# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须支持 Agent 分层记忆记录的最小管理边界

系统必须支持 Agent 分层记忆记录的最小管理边界，以避免长期依赖单一长上下文或将所有记忆混成同一种记录。 The system MUST support a minimal management boundary for layered agent memory records.

#### Scenario: 按 layer 读取记忆记录

- WHEN owner 或平台侧受权能力需要读取某个 Agent 的记忆记录
- THEN 系统必须能够按 layer 返回受控结果
- AND 不同 layer 不得被视为同一种无差别记录

#### Scenario: 写入任务级或摘要记忆

- WHEN 平台侧受控流程需要写入任务级临时记忆或会话摘要记忆
- THEN 系统必须能够通过统一边界保存该记录
- AND 后续生命周期管理不得依赖调用方各自散写

