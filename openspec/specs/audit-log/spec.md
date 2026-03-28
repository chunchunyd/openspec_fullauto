# Audit Log Specification

## Purpose

本规格定义“能干”项目首期权威审计记录层的当前行为真相源。

首期 audit log 能力聚焦于：

- 为关键 Agent 调用和治理动作提供权威留痕
- 记录最小可追踪上下文
- 与 analytics 派生层分离
- 支撑问题复盘、责任确认和合规追溯
## Requirements
### Requirement: 系统必须提供权威的业务审计记录层

系统必须为关键 AI 与治理动作提供权威的业务审计记录层，以支持追溯、责任确认、问题复盘和合规留痕。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖以下记录类型中的全部或核心子集：

- Agent 关键动作
- 关键平台状态变更
- 审核结果
- 治理动作
- 工具调用结果
- 任务失败与关键异常

#### Scenario: 记录关键 Agent 动作

- WHEN Agent 发生生成、发布、修改、回复、工具调用或关键失败等动作
- THEN 系统必须能够记录对应审计记录
- AND 记录必须能够关联 Agent、任务或相关业务对象

#### Scenario: 记录治理动作

- WHEN 系统对对象执行拒绝公开、下线、隐藏或紧急处理
- THEN 系统必须能够记录对应审计记录
- AND 该记录必须能够支持后续追溯动作来源与结果

### Requirement: 系统必须让审计记录具备最小可追踪上下文

系统必须让审计记录具备最小可追踪上下文，避免形成无法解释来源的孤立记录。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持关联以下信息中的全部或核心子集：

- actor
- source
- agent
- task
- 目标业务对象
- 结果状态
- 原因码或错误码
- 发生时间

#### Scenario: 追溯一次关键业务动作

- WHEN 平台需要追溯一次关键 AI 或治理动作
- THEN 审计记录必须能够提供足够的上下文信息
- AND 不得只能依赖调试日志或统计聚合结果反推

### Requirement: 系统必须将审计记录与分析派生层分开

系统必须将审计记录与 analytics 指标聚合层分开处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: analytics 消费审计记录

- WHEN analytics 需要生成指标、看板或趋势结果
- THEN 它可以消费审计记录或基于其派生数据
- AND analytics 本身不应替代审计记录成为权威业务真相源

#### Scenario: 调试日志与审计记录并存

- WHEN 系统同时产生日志、审计记录和分析事件
- THEN 审计记录必须保留权威业务留痕职责
- AND 调试日志或分析事件不得替代其追溯职责

### Requirement: 系统必须为后台审计中心提供受控的查询边界

系统必须为后台审计中心提供受控的查询边界，以便在不改变权威审计记录 owner 的前提下查看关键操作留痕。 The system MUST provide a controlled query boundary for the admin audit center.

#### Scenario: 查询审计记录

- WHEN 具备权限的后台用户按条件查询审计记录
- THEN 系统必须返回符合条件的记录结果
- AND 结果必须保留最小可追溯上下文

#### Scenario: 无权限访问审计中心

- WHEN 不具备相应权限的请求访问审计中心读取边界
- THEN 系统必须拒绝该访问
- AND 不得暴露受限审计字段或原始记录细节

