# Agents Specification

## Purpose

本规格定义“能干”项目首期 Agent 体系的当前行为真相源。

首期 Agent 能力聚焦于：

- 支持干细胞 Agent 与分化细胞 Agent 两类基础形态
- 支持注册用户拥有并管理自己的私有 Agent
- 支持 Agent 的基础资料、角色设定与平台侧策略元数据
- 支持分层记忆与文本知识维护
- 支持 Agent 任务记录与状态跟踪
- 支持 Agent 从私有状态申请公开为 AI IP
- 支持关键 Agent 行为留痕

首期不要求品牌 Agent、群组 Agent、多模态知识导入或完全开放生态作为当前已交付行为，但系统应保留后续扩展空间。
## Requirements
### Requirement: 系统必须支持两类基础 Agent 形态

系统必须支持干细胞 Agent 与分化细胞 Agent 两类基础形态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

干细胞 Agent 用于承接用户初始兴趣与长期协作关系；分化细胞 Agent 用于承接围绕特定兴趣、角色或使用场景形成的专业化能力。

#### Scenario: 创建后识别 Agent 类型

- WHEN 系统创建一个新的 Agent
- THEN 该 Agent 必须被标识为干细胞 Agent 或分化细胞 Agent
- AND 后续能力扩展不得破坏这两类基础形态的区分

#### Scenario: 用户查看自己的 Agent 列表

- WHEN 用户查看自己的 Agent 列表
- THEN 系统必须能够返回每个 Agent 的基础类型信息

### Requirement: 系统必须明确 Agent 所属权与可见性边界

系统必须为每个 Agent 记录所属用户、可见性和公开状态，并据此限制管理权限。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少支持：

- 私有可见
- 公开申请中
- 已公开
- 已拒绝
- 已下线

#### Scenario: 管理自己的私有 Agent

- WHEN 用户访问自己创建的私有 Agent
- THEN 系统必须允许其查看和管理该 Agent 的可管理信息

#### Scenario: 访问他人的私有 Agent

- WHEN 用户尝试访问不属于自己的私有 Agent
- THEN 系统必须拒绝该管理访问

#### Scenario: 查看公开 Agent

- WHEN 一个 Agent 已处于公开可见状态
- THEN 系统必须允许其他用户以公开身份消费该 Agent 的公开能力
- AND 该公开身份必须与其私有管理边界保持区分

### Requirement: 系统必须维护 Agent 基础资料

系统必须为 Agent 维护最小可用的主体资料。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期 Agent 基础资料至少包括：

- Agent 标识
- 所属用户
- 类型
- 名称
- 头像
- 角色设定
- 人格描述
- 专业领域或标签
- 可见性
- 公开状态
- 成熟度
- 创建时间与更新时间

#### Scenario: 创建 Agent 后查看详情

- WHEN 用户创建或查看一个 Agent
- THEN 系统必须返回该 Agent 的基础资料

#### Scenario: 更新 Agent 基础资料

- WHEN Agent 所属用户修改名称、头像、角色设定或人格描述等基础资料
- THEN 系统必须保存更新后的内容
- AND 后续读取必须返回最新生效结果

### Requirement: 系统必须区分 Agent 注册管理与运行时编排职责

系统必须区分平台侧 Agent 注册管理职责与 runtime / adapter 侧运行时编排职责，避免将 `agents` capability 长期演化为内嵌执行引擎。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

`agents` capability 负责：

- Agent 基础资料
- 归属关系与可见性
- 公开申请与成熟度
- policy metadata
- 记忆记录与知识条目管理

runtime / adapter 侧负责：

- prompt 编排
- 模型路由
- 上下文装配
- 工具调用
- 检索执行

#### Scenario: 读取 Agent 管理信息

- WHEN 用户或平台需要读取一个 Agent 的注册、公开、策略或知识管理信息
- THEN 系统必须通过 `agents` capability 提供这些结果
- AND 不应要求调用方依赖 runtime 编排实现细节

#### Scenario: 发起一次运行时协作请求

- WHEN 某个业务流程需要让 Agent 完成一次聊天、生成或训练类协作
- THEN 该流程应通过统一 runtime / task 边界发起请求
- AND 不应把运行时编排职责直接回写成 `agents` capability 的实现承诺

### Requirement: 系统必须支持 Agent 策略配置

系统必须支持以配置化方式维护 Agent 的平台侧策略元数据。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期策略配置至少应覆盖：

- persona 或角色元数据
- 行为边界
- 口吻偏好
- 禁用主题
- 知识使用偏好
- 内容风格偏好

系统应支持策略随场景演进，并允许后续扩展版本化管理。

这些策略元数据用于约束平台侧管理和 runtime 消费边界，但 `agents` capability 不直接承诺 prompt orchestration、模型路由或工具调用实现。

#### Scenario: 查看 Agent 当前策略

- WHEN 用户查看某个 Agent 的策略配置
- THEN 系统必须返回该 Agent 当前生效的策略元数据

#### Scenario: 更新 Agent 策略

- WHEN Agent 所属用户更新行为边界、口吻、禁区或内容风格等策略
- THEN 系统必须保存该更新
- AND 后续通过 Agent 发起的协作流程必须基于更新后的平台侧策略元数据

### Requirement: 系统必须支持分层记忆记录与生命周期管理

系统必须支持 Agent 记忆的分层记录与生命周期管理，避免仅依赖长上下文对话。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少支持以下记忆层：

- 用户长期画像
- Agent 长期设定
- 会话短期上下文或摘要
- 任务级临时记忆

不同记忆层必须允许独立读写和独立生命周期管理。

`agents` capability 负责这些记忆记录的归属和管理边界，但不直接承诺具体 runtime 如何检索、裁剪或装配这些记录。

#### Scenario: 读取不同层级记忆记录

- WHEN 平台侧授权能力需要读取某个 Agent 的记忆记录
- THEN 系统必须能够按层读取相关记忆
- AND 不同层级记忆不得被视为同一种无差别记录

#### Scenario: 写入任务级记忆

- WHEN Agent 完成一次任务并产生临时任务上下文
- THEN 系统必须允许将该内容写入任务级记忆记录
- AND 任务级记忆应允许后续过期、归档或清理

### Requirement: 系统必须支持文本知识维护

系统必须支持用户为 Agent 维护文本型知识条目与其处理状态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期知识维护至少支持：

- 新增文本知识
- 查看知识条目
- 修改知识条目
- 删除知识条目
- 记录知识处理状态或等价元数据

链接摘要、结构化导入、切片、索引和检索编排可作为后续扩展能力，但不属于 `agents` capability 当前直接承诺的执行职责。

#### Scenario: 新增文本知识

- WHEN Agent 所属用户为 Agent 提交一段文本知识
- THEN 系统必须保存该知识条目
- AND 后续该知识应可被查询和管理

#### Scenario: 修改或删除知识

- WHEN Agent 所属用户修改或删除某条知识
- THEN 系统必须更新该知识状态
- AND 后续读取结果必须反映最新状态

### Requirement: 系统必须支持 Agent 任务记录与状态跟踪

系统必须支持记录由 Agent 发起或承接的任务，并跟踪其状态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少支持以下任务类型的统一记录能力：

- 聊天
- 内容生成
- Agent 训练

任务记录至少应包含任务类型、触发来源、状态、结果引用或失败信息。

#### Scenario: 创建 Agent 任务

- WHEN 用户向 Agent 发起聊天、训练或内容生成请求
- THEN 系统必须创建对应任务记录
- AND 任务记录必须具有可追踪状态

#### Scenario: 查看 Agent 任务历史

- WHEN Agent 所属用户查看任务历史
- THEN 系统必须返回该 Agent 的任务记录列表
- AND 每条任务必须包含足以识别执行结果的状态信息

### Requirement: 系统必须支持 Agent 公开申请流程

系统必须支持符合条件的 Agent 从私有状态申请公开为 AI IP。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

公开申请必须与成熟度和审核流程关联，系统不得将未通过流程的私有 Agent 直接视为公开 Agent。

#### Scenario: 发起公开申请

- WHEN Agent 所属用户为一个满足基本条件的 Agent 发起公开申请
- THEN 系统必须记录该申请
- AND 该 Agent 的公开状态必须进入申请中或等待审核状态

#### Scenario: 公开申请被通过

- WHEN Agent 公开申请通过审核
- THEN 系统必须将该 Agent 标记为公开可用状态
- AND 其他用户必须能够以公开 AI IP 的身份看到其公开能力

#### Scenario: 公开申请被拒绝

- WHEN Agent 公开申请未通过审核
- THEN 系统必须保留拒绝结果
- AND 该 Agent 不得进入公开可见状态

### Requirement: 系统必须支持成熟度表达

系统必须为 Agent 维护成熟度信息，用于表达其从私有协作工具成长为公开 AI IP 的准备程度。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

成熟度可以由知识完整度、互动频率、内容稳定性、违规率和用户控制意愿等因素综合形成，但首期至少要能返回一个可被展示和使用的成熟度结果。

#### Scenario: 查看 Agent 成熟度

- WHEN 用户查看某个 Agent 的详情或公开申请前状态
- THEN 系统必须返回该 Agent 的成熟度信息

### Requirement: 系统必须记录关键 Agent 行为日志

系统必须对关键 Agent 行为进行留痕，以满足调试、审计与问题回溯要求。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖以下行为类型：

- 生成
- 发布
- 修改
- 审核命中
- 回复
- 异常失败
- 工具调用
- 公开申请与公开下线

#### Scenario: Agent 执行关键动作

- WHEN Agent 发生关键业务动作
- THEN 系统必须记录对应行为日志
- AND 行为日志必须能够关联到 Agent 与相关任务或业务对象

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

### Requirement: 系统必须允许已登录用户创建私有 Agent 并查看自己的 Agent 列表

系统必须允许已登录用户创建私有 Agent，并以 owner-scoped 方式查看自己的 Agent 列表，而不是要求后续功能在没有“我的 Agent”基线的前提下各自造入口。 The system MUST allow authenticated users to create private agents and list their own agents through an owner-scoped boundary.

#### Scenario: 创建私有 Agent

- WHEN 已登录用户提交合法的最小 Agent 创建信息
- THEN 系统必须为该用户创建一个新的私有 Agent
- AND 新建 Agent 不得默认直接进入公开可见状态

#### Scenario: 查看我的 Agent 列表

- WHEN 已登录用户请求查看自己的 Agent 列表
- THEN 系统必须只返回该用户拥有的 Agent 结果
- AND 列表结果必须包含足以支撑后续选择和管理的最小基础资料

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

### Requirement: 系统必须维护 Agent 平台侧策略 metadata

系统必须维护 Agent 平台侧策略 metadata，以支撑 owner 管理、公开流程前置判断和后续 runtime 消费边界。 The system MUST maintain platform-side agent policy metadata for controlled management and downstream consumption.

#### Scenario: owner 读取当前策略 metadata

- WHEN Agent owner 查看某个 Agent 的管理详情
- THEN 系统必须返回该 Agent 当前生效的策略 metadata
- AND 调用方不应依赖 runtime 私有实现细节才能获取这些管理信息

#### Scenario: owner 更新策略 metadata

- WHEN Agent owner 提交合法的策略 metadata 更新
- THEN 系统必须保存更新后的平台侧策略元数据
- AND 后续管理读取必须返回最新生效结果

### Requirement: 系统必须返回可被公开流程消费的 Agent 成熟度结果

系统必须返回可被公开流程消费的 Agent 成熟度结果，以避免公开申请前长期依赖模糊人工判断。 The system MUST return an agent maturity result that can be consumed by downstream publication workflows.

#### Scenario: 读取 Agent 成熟度

- WHEN owner 或平台侧流程需要判断某个 Agent 的成熟度
- THEN 系统必须返回该 Agent 的当前成熟度结果或等价读模型
- AND 该结果必须能够被后续公开申请边界稳定消费

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

### Requirement: 系统必须支持 Agent 文本知识条目的受控管理

系统必须支持 Agent 文本知识条目的受控管理，以避免知识长期混入 profile 文本或其他不可追踪字段。 The system MUST support controlled management of text knowledge entries for an agent.

#### Scenario: 新增文本知识条目

- WHEN Agent owner 为某个 Agent 提交一段合法文本知识
- THEN 系统必须保存该知识条目
- AND 该条目必须能够在后续被 owner 查询和管理

#### Scenario: 修改或删除知识条目

- WHEN Agent owner 修改或删除既有知识条目
- THEN 系统必须返回反映最新状态的受控结果
- AND 非 owner 不得管理该 Agent 的私有知识条目

### Requirement: 系统必须支持 Agent owner 提交公开申请并读取当前申请状态

系统必须支持 Agent owner 提交公开申请并读取当前申请状态，以便后续审核流可以在稳定申请锚点上继续推进。 The system MUST allow an agent owner to submit a publication application and read its current application status.

#### Scenario: 提交公开申请

- WHEN Agent owner 为一个满足前置条件的 Agent 提交公开申请
- THEN 系统必须记录该申请结果
- AND 该 Agent 不得在未经后续受控流程前直接视为正式公开可见

#### Scenario: 读取公开申请状态

- WHEN Agent owner 查询某个 Agent 的公开申请状态
- THEN 系统必须返回当前申请状态或等价受控结果
- AND 调用方不应依赖 admin 私有实现才能判断该 Agent 是否已处于申请中

