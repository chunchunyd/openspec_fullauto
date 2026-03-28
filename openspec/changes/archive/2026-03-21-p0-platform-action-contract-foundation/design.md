# 设计说明：P0 平台动作契约基建

## 目标

本次设计的目标不是直接实现终局平台，而是先把一条可迁移的边界钉死：

1. 移动端继续只面对现有后端
2. 现有后端通过 `ai-runtime` 与外部 Agent / CLI adapter 交互
3. Agent / adapter 访问平台能力时，必须经过稳定的平台动作契约
4. 平台动作的执行方始终是平台侧，而不是 Agent 自己

## 背景与问题

当前仓库已经出现了一个典型风险信号：

- `packages/job_contracts` 正在长成一套内部 BullMQ 契约
- `ai-runtime`、`llm`、`event-bus` 等更接近未来平台边界的模块却仍是空壳

这意味着如果继续按自然惯性开发，后续最容易形成的是：

```txt
feature -> api service -> queue job / llm client / 临时 adapter
```

而不是：

```txt
feature -> ai-runtime facade -> platform action contract -> adapter / future platform kernel
```

前一种路径短期快，长期迁移代价高；后一种路径更符合你和学长刚达成的共识。

## 目标架构与过渡架构

### 终局方向

终局希望走向：

```txt
App
  |
  v
Platform Kernel
  |-- state mutation
  |-- permission check
  |-- tool/action execution
  |-- workflow orchestration
  |
  v
Agent / model orchestration layer
```

也就是说：

- Agent 负责编排与适配
- 平台内核负责真实业务动作执行

### 前期过渡路径

当前更现实的过渡路径是：

```txt
mobile/app
   |
   v
current api backend
   |
   v
ai-runtime facade
   |
   v
CLI adapter / external agent runtime
   |
   v
model / tool orchestration
```

但关键约束是：

- adapter 不直接碰数据库
- adapter 不直接依赖 Nest 内部 service
- adapter 请求平台能力时，走平台动作契约

## 核心原则

### 1. 平台动作契约独立于内部 transport

平台动作契约不能直接等于：

- BullMQ job name
- Nest controller DTO
- 某个 CLI 命令行参数格式

因为这些都是当前实现细节，不是未来稳定边界。

所以本次 change 要求：

- `packages/platform_action_contracts` 单独存在
- 动作名、请求 envelope、响应 envelope、错误边界、幂等和关联元数据集中维护

### 2. Agent / adapter 只能请求动作，不直接执行平台状态变更

这条是你和学长路线共识里最重要的一条。

举例：

- “创建内容草稿”
- “更新任务状态”
- “登记工具调用结果”
- “写入某类结构化业务状态”

这些都应是平台动作。

Agent / adapter 可以：

- 决定何时请求某个动作
- 提供动作所需输入
- 接收动作结果

但它不应：

- 自己直接写数据库
- 直接调用平台内部 repository / service
- 绕过权限和状态机

### 3. `ai-runtime` 是应用侧反腐层

`apps/api/src/modules/ai-runtime` 应成为应用层进入 AI / adapter 世界的唯一稳定入口。

它的职责应该是：

- 接收来自业务模块的 AI / Agent 相关请求
- 将业务意图映射成平台动作请求或 adapter 请求
- 统一处理 correlation id、幂等键、错误映射与结果透出

它不应继续停留为空目录，也不应被业务模块绕过。

## 建议目录

### 1. 共享平台动作契约：`packages/platform_action_contracts`

建议结构：

```txt
packages/platform_action_contracts/
├─ README.md
└─ src/
   ├─ index.ts
   ├─ action-names.ts
   ├─ action-envelope.ts
   ├─ action-errors.ts
   ├─ action-metadata.ts
   └─ system/
      └─ system-ping.action.ts
```

如果后续要升级为 proto / Connect source of truth，可以在该包内引入：

```txt
proto/
generated/
```

但关键是：source of truth 必须放在这里，而不是散落在 app 内部。

### 2. 应用侧入口：`apps/api/src/modules/ai-runtime`

建议职责：

- `ai-runtime.module.ts`
- `ai-runtime.facade.ts`
- `adapter-client.port.ts` 或等价抽象

让 API 里的业务模块依赖 facade，而不是直接依赖未来 CLI adapter 客户端。

## 首期 envelope 设计

首期建议统一最小 envelope，而不是先上复杂工作流。

### 请求 envelope

至少包含：

- `actionName`
- `actionVersion`
- `correlationId`
- `idempotencyKey`（如适用）
- `actor`
- `source`
- `payload`

### 响应 envelope

至少包含：

- `status`
- `result`
- `error`
- `correlationId`

### 错误边界

至少区分：

- validation error
- permission error
- state conflict
- upstream unavailable
- timeout
- internal error

这样后续不管底层是 CLI adapter、gRPC 还是 Go 平台内核，错误边界都可以保持稳定。

## 首期 smoke action

为了避免抽象空转，本次 change 建议至少定义一个 smoke action。

例如：

- `system.ping`

它的作用不是承载业务，而是验证：

- 平台动作契约本身可以被调用
- `ai-runtime` 可以通过统一 envelope 发起请求
- 后续 transport 可以围绕这个契约演进

注意：

- 这里的 `system.ping` 是平台动作 smoke action
- 它不应被等同为当前 BullMQ 的内部 `system.ping` job

两者名字可以暂时相近，但语义边界必须区分。

## 与 queue 的关系

`packages/job_contracts` 仍然保留其价值，但它是：

- 平台内部异步 transport contract

而 `packages/platform_action_contracts` 是：

- 平台对 adapter / future kernel 演进路径的稳定能力 contract

所以关系应为：

```txt
platform action contract
        |
        v
platform implementation
        |
        +-- sync execution
        \-- queue job (internal)
```

这意味着：

- 平台动作可以内部落成 BullMQ job
- 但 BullMQ job 不应反向变成上层稳定能力契约

## 与事件契约的关系

如果后续 adapter 或 platform kernel 需要状态回传、阶段进度或异步通知，建议：

- `packages/platform_action_contracts`
  - 定义动作请求 / 响应边界
- `packages/event_schema`
  - 定义动作生命周期事件

本次 change 不要求一次性把事件体系做完，但至少要在设计中把这层关系讲清楚，避免以后把事件和动作混在同一包里。

## 与 OpenSpec 现有能力的关系

本次 change 完成后，后续这些能力都会受益：

- `agents`
- `chat`
- `content`
- `moderation`
- `auth` 中未来与 Agent 协作相关的链路

因为这些能力一旦需要 AI / Agent 编排，就不必再直接思考“是调用 Bull job，还是临时接 CLI，还是直接调模型”，而是统一先思考：

- 这是一个什么平台动作
- 它的输入 / 输出 / 权限 / 幂等边界是什么

## 文档与注释要求

本次 change 本身应同步补齐：

- `packages/platform_action_contracts/README.md`
  - 说明职责边界、命名规则、envelope 设计和迁移意图
- 根 README 或相关开发文档
  - 说明这层契约不是 mobile API，也不是内部 Bull job
- 必要注释
  - 解释为什么要把平台动作契约和内部 transport 拆开
