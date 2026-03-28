# Chat Specification

## Purpose

本规格定义“能干”项目首期培养皿与会话系统的当前行为真相源。

首期会话能力聚焦于：

- 用户与 Agent 的一对一会话关系
- 培养皿首页的会话列表
- 历史消息分页加载
- 用户向 Agent 发送文本消息、常用指令或快捷任务
- Agent 回复的异步执行、统一任务跟踪与流式返回
- 消息失败后的重试
- 会话安全约束与上下文控制

首期不要求群聊、语音交互和完整多模态附件能力作为当前已交付行为，但消息结构应保留后续扩展空间。
## Requirements
### Requirement: 系统必须支持用户与 Agent 的一对一会话关系

系统必须支持用户与 Agent 建立一对一会话关系，并以会话为消息承载单元。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期会话关系至少支持：

- 用户与自己的私有 Agent 会话
- 用户与公开 AI IP 会话

#### Scenario: 创建或获取与 Agent 的会话

- WHEN 用户首次与某个可访问的 Agent 发起私聊
- THEN 系统必须创建一条该用户与该 Agent 的会话关系
- AND 后续再次进入同一会话时，系统应返回既有会话而不是重复创建无意义的平行会话

#### Scenario: 访问无权限会话

- WHEN 用户尝试访问不属于自己且不具备公开访问条件的会话或 Agent
- THEN 系统必须拒绝该访问

### Requirement: 系统必须提供 IM 形态的会话列表

系统必须提供培养皿首页所需的会话列表能力，以展示用户与全部相关 Agent 的会话关系。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期会话列表至少应包含：

- 会话标识
- 对应 Agent 基础信息
- 最近消息摘要
- 最近活跃时间
- 未读状态或未读数量

#### Scenario: 查看培养皿首页

- WHEN 已登录用户进入培养皿首页
- THEN 系统必须返回该用户的会话列表
- AND 列表必须能够展示最近消息与未读状态

#### Scenario: 会话排序

- WHEN 一个会话产生新的消息或新的活跃行为
- THEN 系统应能够使该会话在列表中按最近活跃时间更新排序

### Requirement: 系统必须支持历史消息分页加载

系统必须支持在单聊会话中按顺序加载历史消息。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期历史消息至少应支持：

- 按时间或序列稳定排序
- 分页加载
- 返回消息发送方与消息类型

#### Scenario: 首次进入会话加载最近消息

- WHEN 用户首次进入某个会话页面
- THEN 系统必须返回最近一段消息历史

#### Scenario: 向上加载更早消息

- WHEN 用户继续请求更早的历史消息
- THEN 系统必须按稳定顺序返回更早消息
- AND 不得造成消息重复或明显乱序

### Requirement: 系统必须支持发送文本消息

系统必须支持用户在会话中向 Agent 发送文本消息。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

发送消息必须建立在有效登录态和有效会话关系之上。

#### Scenario: 发送普通文本消息

- WHEN 用户在有效会话中提交一条文本消息
- THEN 系统必须创建对应用户消息记录
- AND 系统必须触发该 Agent 的回复处理流程

#### Scenario: 空消息或非法消息

- WHEN 用户提交空内容或不满足基础校验规则的消息
- THEN 系统必须拒绝该发送请求

### Requirement: 系统必须支持常用指令与快捷任务消息

系统必须支持用户通过结构化消息触发常用指令或快捷任务，而不局限于普通文本输入。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持将这类输入作为会话消息的一种合法类型进行记录和处理。

#### Scenario: 发送快捷任务

- WHEN 用户在会话中选择一个快捷任务或常用指令
- THEN 系统必须记录该输入
- AND 系统必须将其纳入 Agent 任务执行流程

### Requirement: 系统必须支持 Agent 回复的异步执行与流式返回

系统不得要求聊天请求始终以同步阻塞方式返回完整 Agent 回复。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期聊天系统必须支持：

- 发送消息后创建统一 Agent 任务或等价统一执行状态
- 通过统一事件边界流式返回 Agent 回复过程或首包结果
- 在结果完成后形成可持久化的 Agent 消息

#### Scenario: 发送消息后等待 Agent 回复

- WHEN 用户成功发送一条消息
- THEN 系统必须为该次回复建立统一可追踪执行状态
- AND 系统必须允许客户端获取流式结果或等价的执行进度

#### Scenario: Agent 回复完成

- WHEN 一次 Agent 回复成功结束
- THEN 系统必须将回复结果写入消息历史
- AND 该结果必须能够关联统一任务记录与流式回流过程

### Requirement: 系统必须支持消息失败兜底与重试

系统必须为发送失败、执行失败或流式失败的消息提供可识别的失败状态，并允许用户发起重试。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

#### Scenario: 消息执行失败

- WHEN 一条消息对应的 Agent 回复因超时、异常或安全拦截而失败
- THEN 系统必须保留该失败结果
- AND 客户端必须能够感知该失败状态

#### Scenario: 用户重试失败消息

- WHEN 用户对失败消息发起重试
- THEN 系统必须重新触发该次消息的处理流程
- AND 新的执行结果必须可被独立追踪

### Requirement: 系统必须控制会话安全与上下文边界

系统必须对会话输入和上下文装配施加基础安全与边界控制。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 敏感内容或高风险输入的基础拦截
- 会话上下文长度控制
- 对异常消息结果的失败兜底

#### Scenario: 输入命中基础风险规则

- WHEN 用户消息命中基础风险规则或不允许输入的内容
- THEN 系统必须阻止其进入正常回复流程，或进入受控处理结果

#### Scenario: 上下文过长

- WHEN 会话历史超过系统允许的上下文装配范围
- THEN 系统必须采用受控方式裁剪、摘要或限制上下文
- AND 系统不得因为上下文无限增长而破坏会话主流程

### Requirement: 系统必须为后续多模态扩展保留消息结构空间

虽然首期会话以文本为主，但系统必须让消息结构具备未来扩展附件或多模态输入的能力。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

这项要求用于约束消息模型，而不是要求首期立即交付完整附件功能。

#### Scenario: 读取消息结构

- WHEN 系统返回会话消息
- THEN 消息结构必须能够区分消息类型
- AND 后续扩展附件字段时不得推翻首期文本消息主模型

### Requirement: 系统必须为 owner-scoped private Agent 单聊持久化受控会话与消息锚点

系统必须为 owner-scoped private Agent 单聊持久化受控会话与消息锚点，以避免培养皿列表、历史消息、任务关联和回复投影长期依赖内存态或 runtime 私有状态。 The system MUST persist controlled conversation and message anchors for owner-scoped private agent chats.

#### Scenario: 首次与私有 Agent 建立单聊锚点

- WHEN 已登录用户首次与自己可管理的 private Agent 发起单聊
- THEN 系统必须能够创建或获得该用户与该 Agent 的受控会话锚点
- AND 后续同一 owner 与同一 Agent 的主单聊不得无约束地产生重复平行会话

#### Scenario: 持久化用户消息与 assistant 消息落点

- WHEN 单聊链路创建一条用户消息或后续 assistant 消息
- THEN 系统必须能够把该消息持久化到受控消息锚点
- AND 消息记录必须能够关联所属会话与基础发送方类型

### Requirement: 系统必须为 owner-scoped private chat 返回最小会话列表与历史读取结果

系统必须为 owner-scoped private chat 返回最小会话列表与历史读取结果，以支撑培养皿首页与单聊页的正式读取主线。 The system MUST return a minimal read model for owner-scoped private chat session lists and message history.

#### Scenario: 查看 private chat 会话列表

- WHEN 已登录 owner 进入培养皿首页
- THEN 系统必须返回该用户可管理的 private chat 会话列表
- AND 列表结果必须包含最近消息摘要与最近活跃时间

#### Scenario: 分页读取 private chat 历史消息

- WHEN 已登录 owner 请求某个 private chat 会话的历史消息
- THEN 系统必须按稳定顺序返回该会话的消息分页结果
- AND 不得允许调用方通过会话标识越权读取他人的 private chat 历史

### Requirement: 系统必须把 owner-scoped private chat 文本发送映射为受控 runtime 调用

系统必须把 owner-scoped private chat 文本发送映射为受控 runtime 调用，以避免 `chat` 只停留在只读历史页而没有正式协作入口。 The system MUST map owner-scoped private chat text sends to a controlled runtime dispatch.

#### Scenario: 发送 private chat 文本消息

- WHEN 已登录 owner 向自己可管理的 private Agent 发送一条合法文本消息
- THEN 系统必须持久化该用户消息并创建或关联统一 Agent task
- AND 平台必须通过共享 runtime provider 发起对应 dispatch

#### Scenario: 无权限或非法输入的发送请求

- WHEN 用户尝试向不具备 owner 访问条件的 Agent 发送消息，或提交空内容/非法内容
- THEN 系统必须在进入 runtime 前拒绝该请求
- AND `chat` 不得把这类业务校验责任下推给 runtime

### Requirement: 系统必须为 owner-scoped private chat 提供受控流式回流与 assistant 消息落地

系统必须为 owner-scoped private chat 提供受控流式回流与 assistant 消息落地，以便聊天回复能够回到正式消息历史主线。 The system MUST provide controlled streaming projection and assistant message persistence for owner-scoped private chat.

#### Scenario: 读取 private chat 回复过程

- WHEN 已登录 owner 读取某次 private chat 回复的流式过程或等价事件结果
- THEN 系统必须返回受控的 chat 语义结果
- AND 不得把 provider 私有事件结构直接作为最终消费接口暴露

#### Scenario: assistant 回复完成并落地

- WHEN 一次 private chat 回复成功完成
- THEN 系统必须将最终 assistant 回复落地为会话历史中的一条消息
- AND 会话的最近消息摘要与最近活跃时间必须随之更新

### Requirement: 系统必须为 owner-scoped private chat 提供失败状态与手动重试边界

系统必须为 owner-scoped private chat 提供失败状态与手动重试边界，以避免培养皿主流程在失败场景下停留在不可恢复的模糊状态。 The system MUST provide controlled failure states and manual retry boundaries for owner-scoped private chat.

#### Scenario: private chat 回复失败

- WHEN 一次 private chat 回复因 dispatch 失败、执行失败、超时或等价异常而未成功完成
- THEN 系统必须保留可读的失败状态与最小失败信息
- AND 该失败结果必须仍然能够关联原始用户消息与统一 Agent task

#### Scenario: owner 手动重试失败消息

- WHEN 已登录 owner 对一条可重试的失败消息发起手动重试
- THEN 系统必须重新进入受控的发送与执行主线
- AND 新的执行结果必须能够与原始失败消息保持可追踪关联

### Requirement: 系统必须让 chat 接口接受平台侧 cuid 标识

系统必须让 chat 相关读取、事件和重试接口接受平台侧 `cuid` 标识，并与 Prisma 主键真相源保持一致。 The system MUST accept platform cuid identifiers in chat API contracts instead of enforcing UUID-only input.

#### Scenario: 使用会话 cuid 读取历史消息

- WHEN 客户端携带一个合法的会话 `cuid` 请求历史消息
- THEN 系统必须允许该请求通过参数校验
- AND 不得在控制器层把该请求误判为非法 UUID

#### Scenario: 使用任务或消息 cuid 读取后续结果

- WHEN 客户端携带一个合法的任务 `cuid` 或消息 `cuid` 请求事件或重试
- THEN 系统必须进入真实的业务校验与权限判断
- AND 不得因为平台主键格式与 DTO 约束不一致而提前返回错误

### Requirement: 系统必须通过受控映射读取 chat 对应的 runtime 任务结果

系统必须通过平台 task 与 runtime task 之间的受控映射读取 chat 事件结果，而不是假设两侧 task 标识天然相同。 The system MUST read chat runtime results through a controlled platform-task-to-runtime-task mapping.

#### Scenario: 发送消息后读取任务事件

- WHEN 平台已经为一条聊天用户消息创建 task 并成功派发到 runtime
- THEN 后续事件读取必须通过该平台 task 对应的 runtime task 关联访问真实结果
- AND 不得依赖“平台 task id 与 runtime task id 恰好相同”的隐式假设

#### Scenario: runtime 映射缺失或失效

- WHEN 平台 task 尚未持有可用的 runtime task 关联，或其关联已经失效
- THEN 系统必须返回受控错误或受控未就绪结果
- AND 不得把错误映射静默伪装成正常的空事件列表

### Requirement: 系统必须通过轮询主线返回受控完成语义并落地 assistant 消息

系统必须通过当前公开的 chat 轮询主线返回受控完成语义，并在成功完成后落地 assistant 消息，而不是只在内部 stream 路径上完成最终投影。 The system MUST expose controlled completion semantics and finalize assistant messages through the polling path that clients actually use.

#### Scenario: 轮询时当前暂无新事件

- WHEN 客户端轮询某个仍在运行中的 chat 任务且当前页没有新增事件
- THEN 系统必须把该结果表达为“当前无新增”或等价未完成状态
- AND 不得把它误报为任务已经完成

#### Scenario: 轮询确认任务成功完成

- WHEN 客户端轮询到某个 chat 任务已经成功完成
- THEN 系统必须把最终 assistant 回复落地为会话消息
- AND 会话最近消息摘要与最近活跃时间必须随之更新

### Requirement: 系统必须让 dispatch 失败状态与重试门禁保持一致

系统必须让 chat dispatch bootstrap 失败后的消息状态、任务状态和重试门禁保持一致，避免真实失败消息被卡在不可重试的半断链状态。 The system MUST keep dispatch failure state projection and retry eligibility consistent for chat messages.

#### Scenario: dispatch bootstrap 失败

- WHEN 平台在持久化用户消息和创建任务后，runtime dispatch bootstrap 失败
- THEN 系统必须把该结果投影为受控的失败消息与失败任务状态
- AND 客户端后续读取历史时必须能够识别该失败结果

#### Scenario: 用户重试真实失败消息

- WHEN 用户对一条因 dispatch 或执行失败而进入可重试状态的消息发起手动重试
- THEN 系统必须允许其进入新的受控任务主线
- AND 不得因为旧的消息状态投影不一致而错误拒绝该重试请求

### Requirement: 系统必须在 dispatch 失败时返回与持久化状态一致的发送结果

系统必须在 chat dispatch bootstrap 失败后立即返回与最新持久化状态一致的发送结果，而不是继续暴露旧的内存排队态。 The system MUST align the immediate send response with the persisted failure projection after dispatch bootstrap failure.

#### Scenario: dispatch bootstrap 失败后的发送首包

- WHEN 平台已经持久化用户消息并创建 task，但 runtime dispatch bootstrap 失败
- THEN `POST /chat/send` 的响应必须返回与最新持久化结果一致的失败消息状态和失败任务状态
- AND 响应中的失败信息不得继续停留在旧的排队态投影

#### Scenario: 客户端基于首包判断失败可重试

- WHEN 客户端收到一次 dispatch bootstrap 失败的发送响应
- THEN 它必须能够直接从该响应识别失败信息与可重试语义
- AND 不得被迫先额外轮询或重读历史才能知道该消息已经进入失败主线

### Requirement: 系统必须在轮询主线中恢复遗漏的 finalize 与 assistant 消息回填

系统必须让 chat polling 主线在 task 已完成但 finalize 尚未完全收口时，能够恢复 assistant 消息、触发用户消息状态和会话读模型，而不是仅以 assistant 消息是否已存在作为 finalize 已完成的判断。 The system MUST recover missed polling finalization by reconciling the assistant message, triggering user-message status, and conversation read model as one controlled completion path.

#### Scenario: finalize 首次失败后再次轮询

- **WHEN** 某次 polling 已经判断 task 完成，但上一次 finalize 或消息落地失败
- **THEN** 后续再次轮询时系统必须能够进入受控恢复路径并再次尝试补齐 assistant 消息或剩余读模型状态
- **AND** 不得因为之前已经错过完成事件而永久放弃 finalize

#### Scenario: 客户端越过完成事件后恢复轮询

- **WHEN** 客户端恢复轮询时，`afterSeq` 已经越过最初的完成事件所在页，但 task 实际已经完成
- **THEN** 系统必须仍然能够识别“task 已完成但 finalize 未全部收口”的状态
- **AND** 必须把 assistant 消息和相关读模型补回正式历史主线，而不是只返回一个没有消息落地或读模型修复的完成标记

#### Scenario: assistant 消息已存在但读模型未收口

- **WHEN** 某次历史失败已经创建了 assistant 消息，但触发用户消息状态仍未进入完成态，或会话最近活跃时间/摘要仍未对齐最终回复
- **THEN** 系统必须继续执行剩余 reconcile，而不是仅因 assistant 消息存在就视为 finalize 已完成
- **AND** 重复恢复不得重复生成新的 assistant 消息

### Requirement: 系统必须让 chat task events 契约与真实返回保持一致

系统必须让 chat task events 的对外契约、文档和导出结果与真实返回结构保持一致，并显式表达受控事件载荷、状态枚举以及未就绪 / 错误语义，而不是继续把差异化结果压扁成同一种 `UNKNOWN` 空页。 The system MUST keep the chat task-events contract aligned with actual response payloads, state semantics, and controlled readiness/error outcomes.

#### Scenario: 文档化增量与完成事件载荷

- **WHEN** 调用方读取 chat task events 契约或 OpenAPI 文档
- **THEN** 它必须能够看到与真实返回一致的 `content.delta`、`content.completed` 或等价正式命名
- **AND** 不得被旧的 `reply.*` 命名误导

#### Scenario: 文档化状态与进度语义

- **WHEN** 调用方依据 task events 契约实现状态解析
- **THEN** 契约必须准确表达实际可能出现的事件状态、进度字段和未知态兜底
- **AND** 不得省略已经在服务真实返回中存在的正式状态值

#### Scenario: runtime 映射缺失时读取 task events

- **WHEN** 平台 task 存在，但该 task 仍未持有可用的 runtime task 关联
- **THEN** task-events 的对外响应必须显式表达这是受控未就绪 / 映射缺失结果
- **AND** 不得把这类情况伪装成与“当前无新增事件”完全相同的普通成功空页

#### Scenario: runtime 暂时不可读时读取 task events

- **WHEN** 平台 task 已存在有效 runtime task 关联，但 runtime 读取过程暂时失败
- **THEN** task-events 的对外响应必须显式表达这是受控的暂时性错误语义
- **AND** 不得只返回没有上下文的 `UNKNOWN` 与空事件数组

### Requirement: 系统必须在 chat 发送与重试响应中返回稳定的任务跟踪元数据

系统必须在 owner-scoped private chat 的发送、重试和等价成功响应中返回稳定的任务跟踪元数据，以便调用方能够直接基于首包或重试结果继续追踪同一条任务主线。 The system MUST expose stable task-tracking metadata in chat send and retry success responses.

#### Scenario: 发送消息后返回任务跟踪字段

- **WHEN** 已登录 owner 成功发起一条 private chat 消息，或请求已落入受控的即时失败态
- **THEN** 系统返回的成功响应必须包含平台 task 标识以及当前可用的任务跟踪字段
- **AND** 调用方不得被迫通过额外源码推断才能确认 `runtimeTaskId`、失败信息或等价追踪字段是否存在

#### Scenario: 重试失败消息后返回任务关联信息

- **WHEN** 已登录 owner 对一条失败消息发起手动重试并成功进入新的任务主线
- **THEN** 系统返回的重试响应必须能够表达新任务与原失败任务之间的追踪关联
- **AND** 该关联不得仅停留在服务内部类型，而不进入正式响应契约

