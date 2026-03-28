# Auth Specification

## Purpose

本规格定义“能干”项目首期认证与会话体系的当前行为真相源。

首期认证能力聚焦于：

- 手机号验证码登录
- 用户协议、隐私政策与 AI 内容告知确认
- access token 与 refresh token 驱动的登录态管理
- 设备会话查看与移除
- 异常登录的基础风险控制
- 退出登录与账号状态约束

首期不要求将微信、Apple ID 等第三方登录作为当前已交付行为，但系统应为后续扩展保留能力空间。
## Requirements
### Requirement: 系统必须支持手机号验证码登录

系统必须支持用户通过手机号与短信验证码完成注册或登录。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

同一手机号在首期应作为唯一身份识别依据之一。对于首次成功验证的手机号，系统必须能够创建可用账号；对于已存在账号的手机号，系统必须能够完成登录。


#### Scenario: 用户通过手机号验证码完成注册或登录

- WHEN 用户提交合法手机号与有效短信验证码进行登录
- THEN 系统必须完成该手机号的身份校验
- AND 系统必须为首次成功验证的手机号创建可用账号，或为既有账号完成登录
### Requirement: 系统必须生成、缓存并发送登录验证码

系统必须支持在登录前为合法手机号生成、缓存并发送一次性验证码，以作为后续身份校验输入。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 请求登录验证码

- WHEN 用户提交合法手机号并请求登录验证码
- THEN 系统必须生成受控的一次性验证码
- AND 系统必须以短期缓存形式保存该验证码
- AND 系统必须通过共享短信发送能力完成发送

### Requirement: 系统必须对验证码发送应用冷却时间与基础发送频控

系统必须对登录验证码发送应用冷却时间与基础发送频控，避免同一手机号或同一请求来源在短时间内重复触发发送。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 冷却期内重复请求

- WHEN 同一手机号仍处于验证码发送冷却期
- THEN 系统不得继续按正常流程重新发送验证码

#### Scenario: 短时间内频繁请求

- WHEN 同一手机号或同一请求来源在短时间内频繁请求验证码
- THEN 系统必须触发基础发送频控
- AND 系统不得继续按正常节奏发送验证码

#### Scenario: 发送验证码

- WHEN 用户提交合法手机号并请求验证码
- THEN 系统必须向该手机号发送短信验证码
- AND 系统必须返回可用于前端倒计时与后续校验的请求结果

#### Scenario: 使用正确验证码登录

- WHEN 用户提交已发送的手机号和有效验证码
- THEN 系统必须完成身份校验
- AND 系统必须为该手机号创建账号或登录已有账号
- AND 系统必须返回登录态建立所需的认证结果

#### Scenario: 使用错误或过期验证码登录

- WHEN 用户提交错误、过期或已失效的验证码
- THEN 系统必须拒绝登录
- AND 系统必须返回可识别的失败结果

### Requirement: 系统必须在首次可用登录前完成必要授权确认

系统必须支持记录并校验用户对用户协议、隐私政策和 AI 生成内容告知的确认状态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

若用户尚未完成必需确认，系统不得将其视为已完成首期可用登录。


#### Scenario: 首次登录前需要确认协议

- WHEN 用户通过验证码完成身份校验，但尚未确认必要协议与告知
- THEN 系统必须要求用户完成确认流程
- AND 系统必须在确认完成后才允许进入完整产品能力

#### Scenario: 已确认用户再次登录

- WHEN 用户此前已经完成必要协议与告知确认
- THEN 系统在后续正常登录时不得重复阻塞主流程
- AND 系统应保留该确认记录用于审计与追踪

### Requirement: 系统必须建立可刷新的登录态

系统必须在登录成功后建立可验证、可续期、可失效的登录态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期登录态必须至少包含：

- access token
- refresh token
- 与设备会话相关的记录信息


#### Scenario: 登录成功后建立会话

- WHEN 用户登录成功
- THEN 系统必须签发 access token 与 refresh token
- AND 系统必须创建对应的设备会话记录
- AND 后续受保护接口必须能够基于登录态识别当前用户

#### Scenario: access token 失效后刷新登录态

- WHEN access token 失效且 refresh token 仍然有效
- THEN 系统必须允许客户端刷新登录态
- AND 刷新后必须返回新的可用认证结果

#### Scenario: refresh token 无效

- WHEN 客户端使用无效、过期或已撤销的 refresh token 请求刷新
- THEN 系统必须拒绝刷新
- AND 客户端必须被视为需要重新登录

### Requirement: 系统必须支持设备会话管理

系统必须支持用户查看当前账号的设备登录状态，并支持移除指定设备的登录态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

设备会话至少应包含设备标识、最近活跃时间和当前状态等可管理信息。


#### Scenario: 查看我的登录设备

- WHEN 已登录用户请求查看设备会话列表
- THEN 系统必须返回该用户当前可管理的设备会话信息

#### Scenario: 移除指定设备

- WHEN 已登录用户主动移除某个设备会话
- THEN 系统必须撤销该设备对应的登录态
- AND 被移除设备后续不得继续使用原有 refresh token 维持会话

### Requirement: 系统必须具备基础异常登录风控

系统必须对登录过程中的明显异常行为提供基础风险控制能力。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 验证码发送频控
- 验证码校验失败次数控制
- 异常设备或异常请求的基础识别与拦截能力


#### Scenario: 短时间内重复请求验证码

- WHEN 同一手机号或同一请求来源在短时间内频繁请求验证码
- THEN 系统必须触发频控或限流
- AND 系统不得继续按正常节奏发送验证码

#### Scenario: 验证码多次校验失败

- WHEN 同一手机号在短时间内多次提交错误验证码
- THEN 系统必须触发基础风险控制
- AND 系统可以临时限制后续登录尝试

### Requirement: 系统必须记录并判定基础登录风险信号

系统必须在认证流程中记录并判定最小请求来源或设备风险信号，并将其用于基础受控限制或受控拒绝。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 请求来源或设备信号明显异常

- WHEN 登录请求命中受控定义下的异常请求来源或异常设备信号
- THEN 系统必须触发基础风险判定
- AND 系统可以对该请求施加受控限制或受控拒绝

#### Scenario: 记录风险判定上下文

- WHEN auth 流程命中风险限制或风险拒绝分支
- THEN 系统必须记录最小结构化上下文
- AND 日志不得直接泄露验证码、完整手机号或完整 token

### Requirement: 系统必须在验证码校验成功后继续执行最小风险判定

系统在验证码校验成功后、返回可用于建立登录态的认证结果前，必须继续执行最小风险判定，而不是仅依赖发码阶段的风险限制。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 验证码正确但请求命中高风险判定

- WHEN 客户端提交正确验证码，但该请求在校验阶段命中受控定义下的高风险条件
- THEN 系统必须对该请求施加受控限制或受控拒绝
- AND 系统不得仅因为验证码正确就直接放行后续登录建立

### Requirement: 系统必须在会话建立前执行最小风险判定

系统在真正创建设备会话并签发登录态前，必须再次执行最小风险判定，以避免高风险请求在最后一步无条件获得登录态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 登录态建立前命中高风险判定

- WHEN 客户端已经完成验证码校验，但请求在会话建立阶段命中受控定义下的高风险条件
- THEN 系统必须拒绝或限制该次会话建立
- AND 系统不得为该请求签发新的有效登录态

### Requirement: 系统必须为 verify 与 session 风险分支记录最小结构化上下文

系统在验证码校验阶段或会话建立阶段命中风险限制 / 风险拒绝时，必须记录最小结构化上下文，以支持排查并保持敏感信息最小暴露。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: verify 或 session 阶段命中风险分支

- WHEN auth 请求在验证码校验阶段或会话建立阶段命中风险限制或风险拒绝
- THEN 系统必须记录最小结构化上下文
- AND 日志不得直接泄露完整手机号、验证码或完整 token

### Requirement: 系统必须支持主动退出登录

系统必须支持已登录用户主动退出当前登录态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

退出登录后，当前会话不得继续被视为有效会话。


#### Scenario: 用户主动退出当前设备

- WHEN 已登录用户发起退出登录
- THEN 系统必须使当前会话失效
- AND 当前设备后续不得继续使用原登录态访问受保护接口

### Requirement: 系统必须根据账号状态限制登录结果

系统必须根据账号状态决定是否允许用户完成登录并进入系统。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应支持对已封禁、已注销或不可用状态账号进行限制。


#### Scenario: 正常账号登录

- WHEN 账号处于正常可用状态
- THEN 系统应允许用户完成登录流程

#### Scenario: 被封禁账号登录

- WHEN 账号处于封禁或不可用状态
- THEN 系统必须拒绝其进入完整产品能力
- AND 系统必须返回可识别的受限结果

### Requirement: 系统必须持久化认证账号状态、授权确认与设备会话主数据

系统必须为认证领域持久化最小可用的账号状态、授权确认和设备会话主数据，以支撑登录判定、协议 gating、refresh token 管理和设备会话治理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应具备以下持久化锚点：

- 账号可用状态
- 必要授权确认记录
- 设备会话记录
- 与 refresh token 撤销或轮换相关的受控持久化信息


#### Scenario: 读取账号状态

- WHEN auth 流程需要判断某个手机号对应账号是否允许继续登录
- THEN 系统必须能够从持久化主数据中读取明确的账号状态

#### Scenario: 读取协议确认状态

- WHEN auth 流程需要判断用户是否已完成必要协议与 AI 告知确认
- THEN 系统必须能够从持久化记录中读取对应确认结果与确认时间

#### Scenario: 建立后续设备会话锚点

- WHEN 后续登录流程需要建立、刷新或撤销设备会话
- THEN 系统必须已经存在可承载该信息的持久化主数据结构

### Requirement: The system MUST issue and maintain refreshable dual-token authentication state

系统必须在登录成功后签发 access token 与 refresh token，并让 refresh token 受到可校验、可轮换、可撤销的会话治理。The system MUST issue access token and refresh token upon successful login, and the refresh token MUST be subject to verifiable, rotatable, and revocable session governance.

#### Scenario: 登录成功后签发双令牌

- WHEN 用户完成受控的身份校验并被允许继续登录 (user completes controlled identity verification and is allowed to continue login)
- THEN 系统必须签发 access token 与 refresh token (the system MUST issue access token and refresh token)
- AND 系统必须将该结果与设备会话记录关联 (the system MUST associate the result with device session record)

#### Scenario: 使用有效 refresh token 刷新

- WHEN 客户端使用仍然有效的 refresh token 请求刷新 (client requests refresh with a still-valid refresh token)
- THEN 系统必须返回新的可用认证结果 (the system MUST return new valid authentication result)

#### Scenario: 使用无效或已撤销 refresh token

- WHEN 客户端使用无效、过期或已撤销的 refresh token 请求刷新 (client requests refresh with invalid, expired, or revoked refresh token)
- THEN 系统必须拒绝刷新 (the system MUST reject the refresh)
- AND 客户端必须被视为需要重新登录 (the client MUST be treated as needing to re-login)

### Requirement: 系统必须在受保护认证接口上校验 access token 与活跃会话状态

系统必须在需要登录态的认证相关接口上校验 access token 的有效性，并确认其关联会话仍处于可用状态。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 缺少或无效 access token 访问受保护接口

- WHEN 客户端在未携带 access token 或携带无效 access token 的情况下访问协议确认、设备会话管理或退出登录等受保护认证接口
- THEN 系统必须拒绝该请求
- AND 系统不得返回受保护用户数据

#### Scenario: 会话已撤销后继续使用旧 access token

- WHEN 某个 access token 关联的会话已经被退出登录、移除设备会话或其他受控撤销操作标记为失效
- THEN 系统必须拒绝该 access token 继续访问受保护认证接口

### Requirement: 系统必须对 auth 接口请求执行最小运行时输入校验

系统必须对 auth 相关接口的最小必填字段、基础类型和明显非法输入执行运行时校验，避免明显坏请求直接落成未处理异常。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 缺少必填字段或字段类型错误

- WHEN 客户端向发送验证码、验证码登录、刷新登录态、协议确认或设备会话治理等 auth 接口提交缺少必填字段或字段类型错误的请求
- THEN 系统必须返回明确的请求校验失败结果
- AND 系统不得因为这类明显坏输入直接返回未处理的 500 错误

### Requirement: 系统必须将公开 OTP 登录入口收敛为可完成会话建立的完整流程

系统对外暴露的手机号验证码登录入口必须能够在成功消费验证码后继续完成登录态建立；系统不得将“只完成验证码校验但无法继续建立会话”的半流程作为当前首期公共登录入口。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 客户端通过公开 OTP 登录入口完成登录

- WHEN 客户端使用公开的手机号验证码登录入口提交合法手机号与有效验证码
- THEN 系统必须在成功校验后继续建立登录态或返回可继续建立登录态的受控结果
- AND 系统不得让客户端停留在已经消耗验证码但无法继续登录的状态

### Requirement: 系统必须接受常见大陆手机号输入格式并统一为单一内部格式

系统必须接受常见大陆手机号输入格式，并在进入 auth 领域后统一归一为单一内部 canonical format，以避免不同层对同一手机号产生不一致处理。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: 使用常见大陆手机号格式请求 auth 接口

- WHEN 客户端使用 `13800138000`、`138 0013 8000`、`138-0013-8000` 或 `+86 138 0013 8000` 等常见格式请求 auth 接口
- THEN 系统必须能够识别这些输入对应的是同一个大陆手机号
- AND 系统必须在内部统一归一为同一手机号格式后再参与验证码、用户识别和会话相关逻辑

### Requirement: 系统必须区分 refresh token 过期与无效

系统在处理 refresh token 时，必须至少区分“refresh token 已过期”和“refresh token 无效或损坏”两类失败结果，避免客户端和排查流程长期依赖模糊错误语义。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: refresh token 已过期

- WHEN 客户端使用已过期的 refresh token 请求刷新登录态
- THEN 系统必须返回明确的已过期失败结果

#### Scenario: refresh token 无效或损坏

- WHEN 客户端使用格式错误、签名无效、被篡改或类型不正确的 refresh token 请求刷新登录态
- THEN 系统必须返回明确的无效 token 失败结果
