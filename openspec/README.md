# OpenSpec

本目录按官方 OpenSpec 模型组织，用来管理“能干”项目的规格真相源与变更提案。

## 这套目录解决什么问题

OpenSpec 的核心不是堆很多说明文档，而是把“当前系统应该怎样工作”和“这次准备怎么改”分开管理：

- `openspec/specs/` 保存当前行为真相源
- `openspec/changes/` 保存尚未归档的变更提案、任务和 spec delta
- `openspec/project.md` 保存跨变更共享的项目上下文、工程约束与协作规则

这样做的目标是先对齐行为，再实施代码修改，最后把变更归档回真相源 specs。

## 当前项目的输入来源

目前本项目的 OpenSpec 主要以以下材料为输入：

- `doc/能干App技术需求文档V0.3.docx`
- `doc/仓库级目录骨架.md`
- `doc/完整目录骨架.md`
- `docs/current-repository-architecture.md`
- `docs/runtime-boundary-refactor-and-unc-wsl-guide.md`

其中：

- `doc/` 保存原始需求、早期目录蓝图和历史参考材料
- `docs/` 保存面向当前开发的架构、运行和操作说明
- `openspec/` 中落下的 `specs/` 与 `changes/` 才是后续研发协作使用的结构化规格体系

## 文档职责分层

- `openspec/specs/`：保存当前系统行为真相源与稳定落位边界，不写 change 协作顺序、提交节奏或实现步骤
- `openspec/changes/`：保存单次变更的 proposal、design、tasks 和 spec delta
- `openspec/project.md`：保存跨 change 共享的项目背景、工程约束和协作规则
- `openspec/CHANGE_START_CHECKLIST.md`：保存开始新 change 前的检查门禁
- `openspec/config.yaml`：保存生成和编写 OpenSpec 时要遵守的项目级规则

## 推荐目录结构

```txt
openspec/
├─ README.md
├─ project.md
├─ specs/
│  └─ <capability>/
│     └─ spec.md
└─ changes/
   └─ <change-id>/
      ├─ proposal.md
      ├─ design.md
      ├─ tasks.md
      └─ specs/
         └─ <capability>/
            └─ spec.md
```

## OpenSpec 写法约定

### 1. 当前规格

`openspec/specs/<capability>/spec.md` 用来描述当前系统行为，而不是实现细节。

推荐结构：

```md
# <Capability> Specification

## Purpose
...

## Requirements
### Requirement: <name>
The system SHALL/MUST ...

#### Scenario: <name>
- WHEN ...
- THEN ...
```

关键点：

- requirement 关注对外行为和约束
- 每个 requirement 至少有一个 scenario
- requirement 文案优先使用 `SHALL` 或 `MUST`

### 2. 变更规格

`openspec/changes/<change-id>/specs/<capability>/spec.md` 用来描述这次变更对当前规格的增量。

推荐结构：

```md
# Delta for <Capability>

## ADDED Requirements
...

## MODIFIED Requirements
...

## REMOVED Requirements
...
```

关键点：

- 新增能力写在 `ADDED`
- 变更既有行为写在 `MODIFIED`
- 删除或废弃能力写在 `REMOVED`

## 推荐工作流

1. 先维护 `openspec/project.md`，明确项目背景、边界和通用约束
2. 按能力建设 `openspec/specs/`，沉淀当前真相源
3. 每做一个新功能或行为变更，就建立一个 `openspec/changes/<change-id>/`
4. 在 change 中补齐 `proposal.md`、`tasks.md`，必要时补 `design.md`
5. change 落地后，把最终结果归并回 `openspec/specs/`

开始任何新 change 前，先使用 [CHANGE_START_CHECKLIST.md](/home/ccyd/workspace/nenggan/openspec/CHANGE_START_CHECKLIST.md) 做一次前置检查。

## 对“能干”项目的当前策略

现阶段仓库已经具备项目上下文、首批 capability 真相源 specs，以及部分已归档的工程基线 change。

后续继续采用“小步 change”的方式推进：

1. 先以现有 `specs/` 对齐当前行为真相源
2. 针对新增需求、返工或重构创建新的 `changes/<change-id>/`
3. 每个 change 尽量聚焦单一子能力或明确 step
4. change 落地后，将最终结果归并回对应 `specs/`

当前已经建立的 capability 包括：

- admin
- agent-runtime-boundary
- agent-tasks
- agents
- analytics
- api-contracts
- audit-log
- auth
- cache
- chat
- content
- event-schema
- feed
- interactions
- moderation
- observability
- platform-actions
- queue
- repository-structure
- runtime-config
- service-health
- sms
- storage

## 当前状态

当前已完成：

- 建立本目录入口说明
- 建立项目上下文文件 `project.md`
- 建立首批 capability 真相源 specs
- 归档部分早期工程基线 change
- 归档 `auth`、`mobile-foundation`、`mobile-auth`、`agents` 等前置系列 change
- 新规划 `chat-part1-step-xx-*` 作为当前活跃 change 系列

当前 `changes/` 目录中同时包含：

- `archive/` 下的历史归档 change
- 按 step 拆分的活跃 change，作为当前后续实现输入

## 当前活跃规划：`chat-part1` 系列

当前拟推进 `chat-part1-step-xx-*`，用于把 `apps/api` 的 `chat` 从空模块推进到“owner-scoped private Agent 单聊主路径可跑通”的第一阶段。

本阶段计划完成：

- 私有 Agent 单聊的会话与消息持久化锚点
- 首次被 `chat` 消费的统一 Agent task 记录锚点
- 培养皿所需的会话列表与历史消息读取
- 文本消息发送、runtime 调用、流式回流与 assistant 消息落地
- 基础失败状态与手动重试边界

本阶段明确留到后续再完成：

- 与公开 AI IP 的私聊边界
- 常用指令、快捷任务消息与 chat -> content 的更深联动
- 未读计数、已读回执、跨设备同步细化与 push 通知
- 敏感输入拦截、上下文裁剪、复杂风控与更完整治理链路
- 多模态附件、语音、群聊、任务取消和其他扩展交互

当前 `chat-part1` 细分 step 为：

- `chat-part1-step-01-session-and-message-data-model-baseline`
- `chat-part1-step-02-agent-task-record-baseline`
- `chat-part1-step-03-session-list-and-history-read-model`
- `chat-part1-step-04-send-message-and-runtime-dispatch`
- `chat-part1-step-05-streaming-event-projection-and-assistant-message-persistence`
- `chat-part1-step-06-failure-state-and-retry-boundary`

下一步建议：在开始新的实现或返工前，先审阅对应 capability 的现有 spec；如果需求已经稳定，再创建或细化本轮工作对应的聚焦 change。
