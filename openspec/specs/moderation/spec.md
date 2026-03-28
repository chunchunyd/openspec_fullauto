# Moderation Specification

## Purpose

本规格定义“能干”项目首期审核与治理体系的当前行为真相源。

首期审核能力聚焦于：

- 对 Agent、消息、帖子、评论等对象执行基础审核
- 支持规则检查、机器审核与人工复核的组合流程
- 支持 Agent 公开申请审核
- 支持内容下线、隐藏与紧急处理
- 支持高风险行为的受控处置
- 支持审核结果与关键治理动作留痕

首期不要求复杂多级审批流或跨区域合规引擎作为当前已交付行为，但系统应保留后续扩展空间。

## Requirements

### Requirement: 系统必须支持对关键对象执行审核

系统必须支持对首期关键业务对象执行审核判断。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖以下对象：

- Agent 公开申请
- 聊天输入或聊天输出
- 帖子内容
- 评论内容


#### Scenario: 提交待审核对象

- WHEN 一个关键对象进入需要审核的流程
- THEN 系统必须能够对该对象执行审核判断
- AND 审核结果必须能够影响后续业务状态

### Requirement: 系统必须支持规则检查、机器审核与人工复核

系统必须支持将规则检查、机器审核与人工复核作为首期审核体系的组成部分。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期可以采用轻量实现，但不得只有单一不可追踪的黑盒判断。


#### Scenario: 命中基础规则

- WHEN 输入、输出或公开对象命中基础风险规则
- THEN 系统必须能够给出通过、待复核或拒绝等受控结果

#### Scenario: 需要人工复核

- WHEN 一个对象无法通过规则或机器审核直接得到最终结论
- THEN 系统必须支持其进入人工复核流程
- AND 在最终结论确定前不得被误视为正常可公开对象

### Requirement: 系统必须支持公开申请审核

系统必须对 Agent 从私有状态转为公开 AI IP 的申请执行审核流程。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

公开申请审核必须独立影响 Agent 的公开状态。


#### Scenario: Agent 发起公开申请

- WHEN 一个 Agent 发起公开申请
- THEN 系统必须能够对该申请执行审核
- AND 审核结果必须能够更新该 Agent 的公开状态

#### Scenario: 公开申请通过

- WHEN Agent 公开申请通过审核
- THEN 系统必须允许该 Agent 进入公开可用状态

#### Scenario: 公开申请被拒绝

- WHEN Agent 公开申请未通过审核
- THEN 系统必须保留该拒绝结果
- AND 该 Agent 不得进入公开可见状态

### Requirement: 系统必须支持内容发布前与发布后的治理

系统必须支持对公开内容执行发布前与发布后的治理控制。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 在发布前拦截需要审核的内容
- 在发布后处理被举报、命中规则或被人工判定违规的内容


#### Scenario: 发布前进入待审核

- WHEN 一条帖子或评论在发布前命中审核条件
- THEN 系统必须将其置为待审核或等价受控状态
- AND 不得将其直接视为正常公开内容

#### Scenario: 已发布内容后置治理

- WHEN 一条已发布内容在发布后被判定存在问题
- THEN 系统必须能够更新其可见状态
- AND 消费侧不得继续将其作为正常公开内容处理

### Requirement: 系统必须支持下线、隐藏与紧急处理

系统必须支持对高风险对象执行下线、隐藏或紧急处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

这类治理能力至少应覆盖公开 Agent、公开帖子和公开评论。


#### Scenario: 常规下线

- WHEN 运营、审核系统或规则引擎判定某对象需要停止公开展示
- THEN 系统必须支持将该对象下线或隐藏

#### Scenario: 紧急处理高风险对象

- WHEN 某个对象构成高风险、违规扩散或平台安全问题
- THEN 系统必须支持紧急处置
- AND 紧急处置结果必须立即影响该对象的公开可见性

### Requirement: 系统必须支持审核结论影响业务状态

系统必须让审核结论能够反映到 Agent、消息、帖子或评论的业务状态中。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

审核结果不得停留在不可执行的旁路记录中。


#### Scenario: 审核通过

- WHEN 一个审核对象通过审核
- THEN 系统必须允许其进入对应的正常业务状态

#### Scenario: 审核拒绝

- WHEN 一个审核对象被拒绝
- THEN 系统必须阻止其进入正常公开流程，或使其退出正常公开状态

### Requirement: 系统必须支持举报与审核联动

系统必须支持将举报结果与审核治理联动起来。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

举报本身不是最终审核结论，但必须能够触发进一步治理流程。


#### Scenario: 用户提交举报

- WHEN 用户对帖子、评论或其他受支持对象提交举报
- THEN 系统必须记录该举报
- AND 系统必须允许该举报进入后续审核或处理流程

#### Scenario: 举报触发治理

- WHEN 举报对象被判定需要进一步处理
- THEN 系统必须支持其进入审核、下线或其他受控状态

### Requirement: 系统必须记录审核结果与治理动作

系统必须对审核过程中的关键结果与治理动作进行留痕，以支持追踪、复盘与责任确认。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应记录：

- 审核对象
- 审核阶段
- 审核结果
- 触发原因或命中规则
- 执行时间
- 执行人或执行来源


#### Scenario: 记录审核结果

- WHEN 系统对一个对象完成审核判断
- THEN 系统必须记录该次审核结果

#### Scenario: 记录治理动作

- WHEN 系统对对象执行下线、隐藏、拒绝公开或紧急处理
- THEN 系统必须记录该治理动作
- AND 后续必须能够追溯该动作的来源与结果
