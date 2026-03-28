# Delta for Agents

## ADDED Requirements

### Requirement: 系统必须持久化最小 Agent registry 主数据与归属锚点

系统必须为 Agent registry 持久化最小主数据与归属锚点，以支撑后续私有管理、public read、知识管理和任务关联能力。 The system MUST persist minimal agent registry data and ownership anchors for downstream agent capabilities.

#### Scenario: 读取 Agent registry 主数据

- WHEN 平台侧需要读取某个 Agent 的 owner、type、visibility、public status 或最小基础资料
- THEN 系统必须能够从受控持久化主数据中返回这些字段
- AND 这些字段不得散落为多个业务模块各自维护的平行真相源

#### Scenario: 后续子能力依赖 Agent registry

- WHEN 后续 CRUD、公开申请、知识条目或记忆记录能力需要关联 Agent
- THEN 系统必须已经存在可复用的 Agent registry 持久化锚点
- AND 后续 step 不得为了补洞临时重建另一套 Agent 主数据结构

