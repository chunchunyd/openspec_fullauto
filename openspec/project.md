# Project Context

## 项目概述

“能干”是一款以 AI Agent 为核心内容主体、互动主体与连接媒介的 AI 社交产品。平台核心链路围绕“创作者身份 -> AI Agent -> IP -> 内容 -> AI Agent -> 接受者身份”展开。

首期目标不是一次性交付全部长期愿景，而是完成一个可运行、可测试、可扩展的第一阶段产品底座，重点验证以下能力：

- 用户与 Agent 的协同成长机制是否成立
- Agent 驱动的内容供给与互动链路是否能够形成闭环
- 系统是否具备后续承载多模态、商业化和开放生态能力的技术基础

## 首期范围

根据 `doc/能干App技术需求文档V0.3.docx` 的定义，首期必须覆盖：

- iOS 与 Android 移动端 App
- 面向移动端的服务端与管理后台
- 用户系统、Agent 系统、内容系统、互动系统、审核系统、基础推荐系统
- AI Agent 调度、记忆、知识、行为日志与内容生成接口
- 数据埋点、基础统计报表、日志监控与部署说明
- 搜索与话题页
- 基础消息推送系统
- Agent 公开审核工作流
- 简版 A/B 实验与推荐策略配置能力

首期明确不作为上线阻塞项：

- 直播、语音聊天室、短视频生产与视频理解
- 完整电商交易闭环
- 海外多语言本地化与国际化运营系统
- 对外开放平台与第三方开发者生态

## 核心概念

- 干细胞 Agent：用户的初始 Agent，负责兴趣记忆、信息收集与整理
- 分化细胞 Agent：围绕特定兴趣或场景形成的专业化 Agent
- 公开 AI IP：达到公开条件并通过审核后对外运营的 Agent
- 能量场：内容消费主页，是 Agent 对外表达的主要场域
- 培养皿：用户管理和训练 Agent 的核心入口，以会话列表形态承载关系与成长过程
- 成熟度：衡量 Agent 是否可从私有协作工具成长为公开 AI IP 的指标

## 主要角色

- 游客
- 注册用户
- 公开 AI IP 主体
- 内容运营人员
- 平台管理员
- 品牌或机构主体（首期预留字段和主体类型）

## 技术栈与架构基线

- 客户端：Flutter，面向 iOS 和 Android 双端
- 服务端：Node.js + NestJS
- Agent Runtime 边界：平台 API + 共享通信基建 + 独立 runtime 服务；当前本地替身为 `apps/agent-runtime-mock`，后续目标为独立 Go runtime
- 主数据库：PostgreSQL
- 缓存与会话：Redis
- 媒体存储：对象存储
- 网关与入口：Nginx 或 API Gateway
- 部署：Docker，后续可扩展到消息队列、搜索引擎、向量数据库与 Kubernetes

架构原则：

- 首期可采用模块化单体或轻量微服务，但必须保持领域边界清晰
- AI 能力不得散落在业务代码中；平台侧必须通过统一的 Agent Runtime 边界接入执行层，而不是在业务模块中直接耦合模型、CLI 或工具执行细节
- 当前 API 与 runtime 的正式通信默认通过共享契约和 gRPC provider；本地 `mock-http` 仅作为兼容调试通道，不作为正式主链路
- `apps/worker` 负责平台内部非 AI 异步作业；Agent 执行类任务应通过独立 runtime 边界处理，不应默认并入 worker 队列
- 推荐引擎与内容服务解耦，便于后续替换更复杂的排序模型
- 所有第三方能力通过适配层封装，避免直接耦合供应商

## 当前已建立的 capability 真相源

当前仓库已经建立的 `openspec/specs/` capability 包括：

- `admin`
- `agent-runtime-boundary`
- `agent-tasks`
- `agents`
- `analytics`
- `api-contracts`
- `audit-log`
- `auth`
- `cache`
- `chat`
- `content`
- `event-schema`
- `feed`
- `interactions`
- `moderation`
- `observability`
- `platform-actions`
- `queue`
- `repository-structure`
- `runtime-config`
- `service-health`
- `sms`
- `storage`

如果一个 change 跨多个领域，应在同一个 change 目录下分别更新多个 capability 的 delta。

## 关键产品与工程约束

- AI 优先，但用户必须保留控制权、配置权与审校权
- 私有 Agent 与公开 AI IP 必须严格区分生命周期和权限边界
- 用户偏好、Agent 记忆、内容表现、互动行为都需要结构化沉淀
- 所有 AI 生成内容、关键 Agent 行为、审核动作与敏感策略命中都必须留痕
- 所有 Agent 调用都必须先通过鉴权、归属校验、可见性校验与必要的业务状态校验，再通过统一 task / event / runtime 边界进入执行层
- runtime 不得直接成为平台业务主数据 owner；平台 API 负责任务创建、事件消费、状态投影和业务结果落地
- 架构必须为语音、视频、直播、电商、海外化等能力预留扩展空间
- 高风险后台操作必须具备权限分级、操作日志与责任追踪

## 非功能要求

- 首期目标支持 1000 至 5000 在线用户，并可平滑扩展
- 常规接口平均响应时间目标不高于 500ms
- 复杂 AI 请求应提供流式反馈，并在 8 秒内给出首包
- 首页内容流首屏加载目标不高于 1.5 秒
- 会话消息发送成功率目标达到 99.9% 以上
- 生产环境必须具备日志、错误监控、性能监控、告警与备份恢复机制
- 至少区分开发、测试、预发、生产四套环境
- 必须遵守中国大陆个人信息保护、网络安全与 AI 内容标识相关监管要求

## 调试与日志约定

- 统一日志基础设施、全局异常接线与调试工作流可以通过独立工程 change 先行建设
- 但具体业务链路的必要日志不得长期集中堆积在“日志基线” change 中
- 后续每个涉及运行时行为、用户主流程、异步任务或外部依赖调用的 change，都应在自身实现范围内主动补充必要的结构化日志
- 日志应优先覆盖关键开始、成功、失败、降级与重试节点，并遵守统一脱敏规则
- 服务端共享日志、trace、health 与可观测性接线应优先沉淀在 `libs/observability` 这类共享运行时层，而不是在单个业务模块内各自复制
- 移动端必须建设独立于服务端 NestJS 实现的日志基础设施；是否抽成移动端共享层可按后续规模决定，但字段命名、trace/correlation id、脱敏和环境区分应尽量与服务端对齐
- 如果某个 change 明显依赖尚未成型的日志基础设施，应优先拆出前置小 change，或在 proposal/design/tasks 中明确记录补齐计划
- 分析埋点、业务真相源留痕与开发调试日志是相关但不同的层次，不得互相替代

## 测试约定

- 后续每个涉及运行时逻辑、状态流转、权限控制、外部服务调用或关键用户主流程的 change，都应显式包含测试任务
- 测试计划应在创建或细化 change 时同步形成，而不是在实现接近完成时再补写
- 测试类型应按变更性质选择，而不应机械限定为单一形式
- 后端纯逻辑、策略、校验与映射优先补单元测试
- 后端接口、数据库读写、权限控制和多组件协作优先补集成测试或等价验证
- 移动端状态管理、纯函数与 service 层优先补单元测试；关键页面流程优先补 widget 测试或等价验证
- 新增或实质修改单元测试、集成测试、widget 测试或等价自动化测试文件时，文件头注释必须写明该测试的完整执行指令，保证接手者能直接运行
- 测试任务应尽量贴近对应 workstream 一起规划；不要长期只把测试集中堆在 tasks 末尾作为收尾动作
- 如果某个 change 暂不适合补自动化测试，任务中必须明确说明原因，并至少保留可重复执行的手动验收步骤

## 前后端契约协作约定

- 当一个工作同时涉及 API 后端与 `mobile` 或 `admin-web` 接入时，应优先稳定 API contract，再推进前端正式接入
- API contract 的共享依据应以最近一次导出的 `packages/api_contracts/openapi/openapi.json` 或由其生成的 client / types 为准
- 临时讨论或口头约定可以用于探索，但不应长期替代已导出的共享契约
- 如果某个 change 同时修改后端接口和前端页面或 service，tasks 中应显式包含 API contract 稳定与 `openapi-export` 的前置步骤

## 注释与文档约定

- change 涉及非直观的状态机、协议映射、缓存语义、队列语义、容错分支、安全边界或其他阅读成本较高的逻辑时，应补充必要的代码注释或模块级说明
- 注释应优先解释约束、边界、原因和易错点，不应机械重复代码表面含义
- 新增或实质修改 `libs/`、`packages/` 这类共享层时，应同步更新对应 README 或等价模块文档，说明职责边界、公开入口、关键依赖、配置和基本用法
- change 如果改变了开发启动方式、环境变量、目录结构、脚本入口、对外契约消费方式或人工操作流程，应在同一 change 中同步更新根 README 或相关入口文档
- 必要注释、模块文档和 README 更新应视为 change 的正式交付内容，而不是收尾阶段可做可不做的附加项

## 仓库协作约定

- `openspec/` 作为独立 Git 仓库维护；主项目仓库跟踪一个指向外部规格仓库的 `openspec/` 符号链接
- OpenSpec 真相源与变更提案允许在独立规格仓库中持续演进，不要求与主项目代码仓库完全同节奏提交
- 主项目代码 worktree 会自动继承该 `openspec/` 符号链接；自动化脚本只校验它存在，不应在子 worktree 内重新创建、替换或覆盖该链接
- 主项目代码仓库应采用按 change 拆分的分支策略；一个可实施的小 change 原则上对应一个独立实现分支
- 主项目代码仓库默认使用 `main` 作为稳定发布分支，`dev` 作为当前集成主线；具体功能开发不应长期直接在 `dev` 上进行
- 当同一功能主题按 `xxx-step-xx-*` 拆成系列 change 时，应将 `step-xx` 之前的前缀视为 series prefix，例如 `mobile-foundation-step-03-network-contract-and-request-pipeline` 的 series prefix 是 `mobile-foundation`
- 系列化 change 应先从最新 `dev` 切出或同步 `series/<series-prefix>` 集成分支；若当前在规划 `step-01`，应把创建 `series/<series-prefix>` 视为系列启动动作
- 系列内的每个 step，包括 `step-01`，都应从 `series/<series-prefix>` 再切出 `feat/<change-id>`、`fix/<change-id>` 或 `chore/<change-id>` 之类的实现分支；非系列 change 再按原规则直接从最新 `dev` 切出实现分支
- 如果一组 change 计划通过 `auto_apply.sh` 以多个 `--prefix` 并行执行，这些 series 必须彼此独立，不得在依赖图中交叉引用
- 如果多个 change 系列实际上围绕同一个目标能力相互依赖，应在创建 change 时直接合并成一个以目标命名的 `series prefix`，而不是先拆成多个系列再在依赖图中交叉引用
- 对系列 change，“切出实现分支”是强制前置门禁：在 detached `HEAD` 或 `series/<series-prefix>` 状态下，不允许开始任何实现性编辑、生成器、格式化、构建或可能写文件的测试动作
- 在主项目仓库开始任何实现性编辑前，应先确认当前分支不是 `dev` 或 `main`，且分支名已显式包含对应 change id；如果仍停留在 `dev` / `main`，应先切出实现分支再继续
- 对系列 change，主工作区或子 worktree 一旦短暂切到 `series/<series-prefix>` 做同步或最终 merge，完成后必须立即切离该分支；若 worktree 需要保留，默认应 detach 到新的集成提交，不允许长期占用系列集成分支
- 如果准备开始某个 change 时主项目工作树已经存在与该 change 无关的未提交改动，应先暂停实施并整理范围边界，避免在脏工作树上直接叠加新的 change
- 当同一 capability 已经拆成多个 `step-xx` 小 change 时，不应继续在同一代码分支内混合实现多个独立 step
- 主项目代码分支名应显式包含 change id；功能实现优先使用 `feat/<change-id>`，修复类改动可使用 `fix/<change-id>`，工程或脚本类改动可使用 `chore/<change-id>`
- 单个 change 的实现过程中，每完成一个或少数几个紧密相关的 task，应及时提交一次，避免长时间堆积大块未提交改动
- 如果是续跑或接手已有 worktree，开始前应先检查当前实现分支上的 staged / unstaged / untracked 改动；这些改动默认视为该 change 的继承现场，应在其基础上继续或安全清理，不要直接忽略
- 不应在没有阶段性提交的情况下连续跨越多个 workstream；当某一小段实现已经达到“可运行、可验证或可回退”的状态时，应优先形成一次提交
- 如果实施过程中已经误在 `dev` 上开始编码或累积了较大未提交改动，应尽快停止继续扩散，在说明当前状态后立即切出与 change id 对应的分支并恢复小步提交节奏
- 系列 step 的 `feat/<change-id>`、`fix/<change-id>` 或 `chore/<change-id>` 在达到可验收状态后，应先合并回 `series/<series-prefix>`；非系列 change 才直接合并回 `dev`
- 当系列 step 准备切回或回合并到 `series/<series-prefix>` 前，实现分支应由 agent 自己提交有效改动并保持工作区干净
- 小 change 合并回上级集成分支前，至少应完成对应实现、自检、必要的契约或脚本更新，以及与该任务相关的 OpenSpec 同步
- 合并到上级集成分支时默认优先使用 `--no-ff merge`，保留实现分支上的阶段性提交历史，同时让一个可实施小 change 对应一个清晰、可追踪的 merge 提交
- `series/<series-prefix>` 回合并到 `dev` 不属于 AI 或自动化代理的默认职责，应由人工把关并执行
- `dev` 到 `main` 的发布合并不属于 AI 或自动化代理的默认职责，应由人工把关并执行
- 如果一次任务同时修改了主项目实现与 `openspec/` 规格，则应分别在主项目仓库与 `openspec` 仓库提交
- 如果一次任务只修改了其中一侧，则只需要提交对应仓库，不要求机械地双提交
- 当任务达到可同步状态时，应优先将两侧提交都推送到各自远端，并在任务说明中标明相关 change id 或对应提交关系
- 两侧提交说明应尽量使用相同的 change id、任务名或可追踪标识，避免规格与实现失联
- 由 AI 或自动化工具生成的 Git 提交不得附带 `Co-authored-by`、`Generated-by` 或等价协作署名尾注，提交信息应保持简洁且可追踪

## OpenSpec 编写约定

- `specs/` 只写当前行为真相源，不写“打算怎么做”
- `changes/` 用于描述某次变更提案、设计、任务与 spec delta
- 在拆分或创建 change 前，应先检查该能力是否依赖 `libs/` 中的共享运行时服务，或 `packages/` 中的共享契约产物
- 如果所需共享层只是占位目录、空文件或明显未完成状态，不应默认视为“已经可复用”；应优先拆出前置小 change，或在当前 change 中显式纳入补齐任务
- 如果同一功能主题需要一次性规划多个 `step-xx` change，应在整组 change 都生成完成后补 `openspec/auto/deps/deps.<series-prefix>.json` 依赖图，供自动化脚本按真实阻塞关系并行调度
- 如果打算让多个 series 一起通过 `auto_apply.sh` 执行，应先确认这些 series 之间不存在交叉依赖；一旦存在交叉依赖，应回到 change 规划阶段，把它们合并成一个以目标能力命名的 `series prefix`
- 当系列分支、依赖图和自动化调度规则已经明确时，change 粒度应优先收束到单一主目标；如果标题需要并列列出多个主产物，默认继续拆分，除非这些内容无法独立实现和验收
- `tasks.md` 只把可执行、可验收、完成后需要勾选的动作写成 checkbox；人工职责说明、范围排除、非本 change 操作和流程性备注必须写成普通项目符号或备注段落，避免 agent 被不可执行说明卡住
- 对 `xxx-step-xx-*` 系列 change，`tasks.md` 头尾的 Git 门禁与收口必须使用固定模板，供 `openspec/auto/auto_apply.sh` 自动识别：头部保留 `自动化确认系列集成分支 ... 已就绪` 与 `自动化从 ... 切出 <implementation-branch> 实现分支` 两条 checkbox；结尾保留 `自动化将 <implementation-branch> merge 回 series/<series-prefix>，保留实现分支上的阶段性提交历史` 这条 checkbox，禁止自由改写句式
- `tasks.md` 的验收 / 验证部分默认应显式加入 ESLint 验收和 TypeScript 验收，并分别引用主仓库 `docs/eslint-style-notes.md` 与 `docs/tsc-fix-summary.md`；如果当前 change 不适用其中某项，必须在任务里写明原因，不能静默省略
- requirement 应描述外部行为、约束或系统承诺，而不是代码实现方式
- 每个 requirement 至少提供一个 scenario
- 对既有行为的变更，应在 delta 中给出完整更新后的 requirement 文本
- 文档默认优先服务 P0 闭环，P1 和长期预留在不阻塞首期的前提下表达

## OpenSpec 文档职责分层

- `specs/` 只承载当前行为真相源与稳定落位边界，不承载 change 协作顺序、提交节奏、README 更新义务或实现步骤
- `changes/` 承载本次准备如何修改系统，包括 proposal、design、tasks 和 spec delta
- `project.md` 承载跨 capability 共享的项目背景、工程约束和协作规则
- `CHANGE_START_CHECKLIST.md` 承载开始新 change 前的检查门禁
- `openspec/docs/` 承载本项目独立于 OpenSpec 官方文档的流程治理、分支策略、依赖图和自动化使用规则
- `docs/` 保存当前开发者说明；`doc/` 保存原始需求、目录蓝图和早期参考材料
- 如果代码现实尚未形成稳定行为，不要把目标蓝图或希望状态提前写成当前 requirement

## 当前建设策略

当前仓库已经形成首批 OpenSpec 真相源，并沉淀了部分已归档的工程基线 change。后续建设应采用以下方式推进：

1. 先以现有 `specs/<capability>/spec.md` 作为当前行为对齐基线
2. 在拆分 change 前，先检查是否依赖现有 `libs/` 共享服务或 `packages/` 共享契约，以及这些共享层是否已经达到可复用状态
3. 如果共享层缺失、只是占位结构或成熟度不足，应优先拆出前置小 change 先补齐基础设施或共享契约
4. 对新增需求、返工、重构或补洞创建新的 `changes/<change-id>/`
5. 对已经做过但需要重做的能力，应新开 change，不直接把旧 change 继续当作当前实施计划
6. 每个 change 尽量聚焦单一子能力或明确 step，保持变更清晰可审阅
7. change 完成后，应及时将最终结果回写到对应 specs，再按规则归档

## 来源说明

当前 `project.md` 基于以下材料整理：

- `doc/能干App技术需求文档V0.3.docx`
- `doc/仓库级目录骨架.md`
- `doc/完整目录骨架.md`
- `docs/current-repository-architecture.md`
- `docs/runtime-boundary-refactor-and-unc-wsl-guide.md`

如根需求基线更新，应优先同步本文件与相关 capability specs。
