# Analytics Specification

## Purpose

本规格定义“能干”项目首期数据采集、分析信号与基础指标能力的当前行为真相源。

首期 analytics 能力聚焦于：

- 客户端关键行为埋点
- 服务端关键运行与业务事件采集
- 消费 Agent 关键行为审计与运行事件
- 统一事件字典与属性口径
- 支撑后台看板的核心指标输出

首期不要求复杂实时数据平台、自助分析系统或完整归因体系作为当前已交付行为，但系统应保留后续扩展空间。
## Requirements
### Requirement: 系统必须支持客户端关键行为埋点

系统必须支持客户端对首期关键用户行为进行埋点采集。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖以下客户端行为中的全部或核心子集：

- 首页曝光
- 内容点击
- 停留时长
- 滑动
- 点赞
- 评论
- 收藏
- 分享
- 私聊发起
- Agent 切换

#### Scenario: 客户端上报关键行为

- WHEN 用户在客户端完成一个受支持的关键行为
- THEN 系统必须能够接收并记录该行为事件

### Requirement: 系统必须支持服务端关键事件采集

系统必须支持服务端对首期关键业务和运行事件进行采集。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖以下服务端事件中的全部或核心子集：

- Agent 生成成功率相关事件
- Agent 平均响应时长相关事件
- 审核命中率相关事件
- 内容发布量相关事件
- 自动回复转化率相关事件

#### Scenario: 服务端记录关键运行事件

- WHEN 一个关键业务动作或运行过程完成
- THEN 系统必须能够记录对应的服务端事件结果

### Requirement: 系统必须支持统一事件字典

系统必须为首期埋点与事件采集建立统一事件字典，避免研发、运营和后台看板口径漂移。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

统一事件字典至少应定义：

- 事件名称
- 事件含义
- 关键属性
- 属性口径
- 版本或变更管理方式

事件字典真相源位于 `docs/tracking/event-dictionary.md`。

#### Scenario: 查询事件定义

- WHEN 研发、测试或运营需要确认一个事件的含义
- THEN 系统必须存在可被统一引用的事件定义来源
- AND 该来源必须说明事件名称、属性口径和最小上下文要求

#### Scenario: 事件变更

- WHEN 一个已有事件或属性口径发生变化
- THEN 系统必须能够记录该变更
- AND 不得以隐式改名或私下变更方式导致口径失真

### Requirement: 系统必须支持消费 Agent 关键行为分析信号

系统必须能够消费 Agent 的关键行为审计记录、平台事件或等价结构化运行信号，用于指标与分析结果产出。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 生成
- 发布
- 修改
- 审核命中
- 回复
- 工具调用
- 异常失败

analytics 可以依赖审计记录层或事件层作为上游输入，但不得把 analytics 自己演化为权威业务留痕 owner。

#### Scenario: Agent 执行关键业务动作

- WHEN Agent 发生一次关键业务动作
- THEN analytics 必须能够消费对应分析信号
- AND 该信号必须能够关联 Agent、任务或业务对象

### Requirement: 系统必须支持指标聚合结果输出

系统必须支持将埋点与日志沉淀为首期核心指标结果，以供后台看板和运营分析使用。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持输出以下指标中的全部或核心子集：

- 新增
- 留存
- DAU
- 内容产量
- 互动率
- 会话转化率
- 公开 IP 数量
- 违规率

#### Scenario: 输出看板指标

- WHEN 后台请求首期核心指标总览
- THEN 系统必须能够返回对应指标结果或等价汇总结果

### Requirement: 系统必须让行为事件具备可追踪上下文

系统必须让客户端事件、服务端事件和行为日志具备最小可追踪上下文。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持关联以下信息中的全部或核心子集：

- 用户
- Agent
- 目标对象
- 事件时间
- 来源页面或来源场景
- 会话或请求链路标识

#### Scenario: 追踪一次行为事件

- WHEN 系统记录一个关键行为事件
- THEN 该事件必须能够关联到足够的上下文信息
- AND 不得成为无法解释来源的孤立记录

### Requirement: 系统必须支持审核与治理相关事件留痕

系统必须对审核命中、下线、拒绝公开、紧急处理等治理相关事件保留可分析记录。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 记录审核或治理事件

- WHEN 一个对象进入审核命中、下线或其他治理动作
- THEN 系统必须保留相应事件或日志记录

### Requirement: 系统必须支持数据采集失败的受控处理

系统必须允许埋点、事件或日志采集在失败时采用受控处理，而不得破坏主业务流程。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期允许事件采集异步化、重试或降级，但不得因为分析链路异常阻塞核心用户链路。

#### Scenario: 埋点链路异常

- WHEN 事件采集或日志写入发生异常
- THEN 系统必须允许主业务流程继续
- AND 系统应采用受控方式进行重试、降级或失败记录

### Requirement: 系统必须区分分析信号与业务真相源

系统必须将分析类事件、权威审计记录与业务主状态区分处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

分析结果可以服务于推荐、看板和优化，但不得替代认证、内容状态、审核状态和权威审计记录等业务真相源。

#### Scenario: 分析数据与业务状态不一致

- WHEN 分析侧统计结果与业务主状态存在延迟或聚合差异
- THEN 系统必须以业务真相源为准
- AND 分析侧结果不得直接覆盖业务主状态

### Requirement: 系统必须维护统一的首期事件字典真相源

系统必须维护统一的首期事件字典真相源，以约束事件命名、属性口径、最小上下文和版本变更规则。 The system MUST maintain a single source of truth for the initial analytics event dictionary.

#### Scenario: 查询事件定义

- WHEN 研发、测试或运营需要确认某个事件的定义
- THEN 系统必须存在统一可引用的事件字典来源
- AND 该来源必须说明事件名称、属性口径和最小上下文要求

#### Scenario: 调整事件口径

- WHEN 一个已有事件或属性口径发生变化
- THEN 系统必须记录该变化
- AND 不得以隐式改名或私下修改方式导致口径失真

### Requirement: 系统必须提供原始分析事件接收与 append-only 存储锚点

系统必须提供原始分析事件接收与 append-only 存储锚点，以统一承接后续客户端埋点和服务端事件发射。 The system MUST provide a raw analytics event ingestion boundary and append-only storage anchor.

#### Scenario: 写入合法原始事件

- WHEN 调用方提交一个符合定义的原始分析事件
- THEN 系统必须能够接收并持久化该事件或其等价结果
- AND 该事件必须保留最小可追踪上下文

#### Scenario: 输入缺少必要上下文

- WHEN 调用方提交的事件缺少必要上下文或不符合最小契约
- THEN 系统必须拒绝该输入或采用受控失败语义
- AND 不得让不可解释的脏数据直接进入权威原始事件存储

### Requirement: 系统必须通过非阻塞的服务端发射边界记录分析事件

系统必须通过非阻塞的服务端发射边界记录分析事件，并在写入失败时保护主业务流程继续执行。 The system MUST emit server-side analytics events through a non-blocking boundary.

#### Scenario: 服务端流程发射分析事件

- WHEN 一个受支持的服务端业务流程完成关键动作
- THEN 系统必须能够通过统一 emitter 记录相应分析事件
- AND 该事件必须携带最小可追踪上下文

#### Scenario: 分析写入失败

- WHEN analytics 写入或下游存储发生异常
- THEN 系统必须允许主业务流程继续
- AND 系统必须以受控方式记录失败或降级结果

