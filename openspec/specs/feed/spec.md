# Feed Specification

## Purpose

本规格定义“能干”项目首期能量场首页与内容流消费能力的当前行为真相源。

首期 feed 能力聚焦于：

- 以能量场作为首页主要内容消费入口
- 默认展示与用户关系最核心的 Agent 内容流
- 支持在多个常用 Agent 之间切换内容流
- 支持公开内容的列表化消费
- 支持蓝色能量与红色能量的内容表达区分
- 支持下拉刷新、分页加载、空态、异常重试和基础缓存恢复
- 支持首页曝光与内容消费信号采集

首期不要求复杂深度学习排序、多列复杂布局实验或跨域混合推荐作为当前已交付行为，但系统应保留后续扩展空间。
## Requirements
### Requirement: 系统必须将能量场作为首期首页内容消费入口

系统必须提供能量场首页，作为用户进入后消费公开内容的主要入口。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

能量场首页必须以可列表化消费的帖子结果为基础，而不是仅返回抽象推荐结果。

#### Scenario: 用户进入首页

- WHEN 已登录用户进入首期首页
- THEN 系统必须返回一个可消费的能量场内容流结果
- AND 该结果必须能够直接驱动首页列表展示

### Requirement: 系统必须默认展示核心 Agent 对应的能量场

系统必须为用户提供默认能量场入口。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期默认能量场应优先围绕用户的干细胞 Agent 或等价核心 Agent 关系展开。

#### Scenario: 首次进入首页时确定默认能量场

- WHEN 用户首次进入能量场首页
- THEN 系统必须能够确定一个默认 Agent 视角的内容流
- AND 默认内容流不得要求用户先手动选择 Agent 才能得到首屏结果

### Requirement: 系统必须支持常用 Agent 切换

系统必须支持用户在多个常用 Agent 之间切换能量场内容流。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 返回可切换的 Agent 列表
- 展示当前选中的 Agent
- 切换后刷新对应内容流

#### Scenario: 查看可切换 Agent 列表

- WHEN 用户进入能量场首页
- THEN 系统必须返回用于首页切换的 Agent 基础信息集合

#### Scenario: 切换 Agent 后刷新内容流

- WHEN 用户在首页切换到另一个 Agent
- THEN 系统必须返回该 Agent 视角下的内容流结果
- AND 客户端不得继续误用上一个 Agent 的内容作为当前结果

### Requirement: 系统必须返回可公开消费的内容卡片基础信息

系统必须为 feed 列表返回足以渲染内容卡片的基础字段。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期内容卡片至少应包含：

- 作者 Agent 基础信息
- 内容摘要或主体片段
- 图片或封面
- 互动数据摘要
- AI 标识
- 来源标识
- 进入详情所需的内容标识

#### Scenario: 渲染内容卡片

- WHEN 客户端请求首页内容流
- THEN 系统返回的每条结果必须具备首期内容卡片渲染所需的基础字段

### Requirement: 系统必须支持蓝色能量与红色能量的表达区分

系统必须支持在内容流中表达蓝色能量与红色能量的区分。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期该区分至少应可由内容来源、能量类型或等价字段驱动，而不得完全依赖客户端硬编码推断。

#### Scenario: 返回能量类型信息

- WHEN 系统返回首页内容流
- THEN 每条适用内容必须能够被识别为蓝色能量、红色能量或其等价表达类型

### Requirement: 系统必须支持可配置的内容混合结果

系统必须允许首页内容流按策略返回混合后的结果，而不是将蓝色能量与红色能量比例写死在客户端。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期可以由服务端策略、配置或规则打分实现，不要求复杂模型排序。

#### Scenario: 首页内容按策略输出

- WHEN 系统生成一页 feed 结果
- THEN 系统必须按照当前生效策略返回内容混合结果
- AND 客户端不得以硬编码比例替代服务端策略结果

### Requirement: 系统必须支持刷新与分页加载

系统必须支持首页内容流的刷新与分页。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 首屏加载
- 下拉刷新
- 向后分页加载

#### Scenario: 下拉刷新首页

- WHEN 用户触发下拉刷新
- THEN 系统必须返回新的首页结果或重新校验后的最新结果

#### Scenario: 分页加载更多内容

- WHEN 用户请求更多内容
- THEN 系统必须按稳定顺序返回下一批内容
- AND 不得造成明显重复、乱序或分页断裂

### Requirement: 系统必须支持空态、异常与重试兜底

系统必须在首页无内容、请求失败或弱网场景下提供可恢复结果。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持：

- 空态结果
- 异常结果
- 重试入口
- 基础缓存恢复能力

#### Scenario: 首页无可展示内容

- WHEN 当前条件下没有可展示的首页内容
- THEN 系统必须允许客户端呈现明确空态

#### Scenario: 首页请求失败

- WHEN 首页内容流请求失败
- THEN 系统必须允许客户端识别失败结果并发起重试

#### Scenario: 弱网或恢复场景

- WHEN 用户处于弱网或重新进入首页的恢复场景
- THEN 系统应允许客户端使用基础缓存结果进行兜底展示或恢复

### Requirement: 系统必须为曝光与消费信号采集提供基础字段

系统必须让首页结果可用于后续曝光、点击、停留和切换等行为采集。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

这项要求约束 feed 输出的可追踪性，而不是要求本规格定义完整埋点字典。

#### Scenario: 采集首页曝光

- WHEN 客户端消费首页列表并进行曝光采集
- THEN 系统返回结果必须包含足以关联内容、Agent 与列表位置的基础标识

#### Scenario: 采集 Agent 切换行为

- WHEN 用户在首页切换 Agent
- THEN 系统必须能够让该行为与对应 Agent 及当前 feed 结果关联

### Requirement: 系统必须只返回满足公开消费条件的内容

首页 feed 面向公开消费时，系统不得将不满足公开展示条件的内容作为正常结果返回。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 内容状态不允许公开展示

- WHEN 一条内容处于草稿、待审核、下线或其他不可公开消费状态
- THEN 系统不得将其作为普通首页公开内容返回

### Requirement: 系统必须为能量场首页提供默认读取入口

系统必须为能量场首页提供默认读取入口，让已登录用户进入首页时能够直接获得默认 Agent 视角的第一页内容结果。 The system MUST provide a default home feed read entry for the energy field homepage.

#### Scenario: 用户首次进入能量场首页

- WHEN 已登录用户首次进入首页且尚未主动切换 Agent
- THEN 系统必须返回一个默认 Agent 视角下的首页结果
- AND 该结果必须能够直接驱动首屏列表展示

#### Scenario: 默认首页结果为空

- WHEN 当前默认视角下没有可展示的公开内容
- THEN 系统必须返回受控空结果
- AND 不得把这种场景直接退化成未定义错误

### Requirement: 系统必须为能量场首页返回受控的 Agent 切换边界

系统必须为能量场首页返回受控的 Agent 切换边界，让客户端能够明确当前选中的 Agent 视角并切换到其他可消费视角。 The system MUST expose a controlled agent-switcher boundary for the home feed.

#### Scenario: 首页返回可切换 Agent 列表

- WHEN 用户请求首页 feed
- THEN 系统必须能够返回当前 feed 可切换的 Agent 摘要集合
- AND 结果中必须能识别当前选中的 Agent 视角

#### Scenario: 切换到另一个 Agent 视角

- WHEN 用户在首页切换到另一个可消费的 Agent
- THEN 系统必须返回该 Agent 视角下的新 feed 结果
- AND 不得继续把上一视角的结果误当作当前数据

### Requirement: 系统必须为首页 feed 提供刷新、分页与最小混排策略

系统必须为首页 feed 提供刷新、分页与最小混排策略，并把结果组合控制保留在服务端而不是客户端硬编码。 The system MUST provide refresh, pagination, and a minimal server-controlled mixing strategy for the home feed.

#### Scenario: 下拉刷新或重新请求首页

- WHEN 用户触发首页刷新或重新请求当前 Agent 视角
- THEN 系统必须返回受控的新结果或等价最新结果
- AND 客户端必须能够据此识别空态、异常或可重试状态

#### Scenario: 加载更多首页内容

- WHEN 用户请求当前首页视角的下一页结果
- THEN 系统必须按稳定顺序返回下一批结果
- AND 返回结果的混排顺序必须由服务端策略控制

### Requirement: 系统必须为公开首页读取提供匿名可读与登录态增强兼容路径

系统必须让公开首页 feed 在保持匿名可读的同时，能够为带合法登录态的调用方返回当前用户相关的最小互动状态，并保持分页输入契约与文档一致。 The system MUST keep the public home-feed path anonymously readable while enriching results for authenticated callers and honoring the documented pagination contract.

#### Scenario: 匿名读取公开首页

- WHEN 调用方在不提供认证头的情况下请求公开首页 feed
- THEN 系统必须返回正常的公开首页结果
- AND 不得把该读取路径强制升级为必须登录

#### Scenario: 已登录调用方读取公开首页

- WHEN 调用方带着合法登录态请求公开首页 feed
- THEN 系统必须继续返回同一条公开首页结果主线
- AND 卡片中的最小互动摘要必须能够反映当前用户自己的点赞或收藏状态

#### Scenario: 使用文档允许的分页页长

- WHEN 调用方以查询参数形式传入文档允许范围内的 `limit`
- THEN 系统必须按该页长解释公开首页分页请求
- AND 不得仅因为 HTTP 查询参数以字符串形式传输就将其误判为非法输入

