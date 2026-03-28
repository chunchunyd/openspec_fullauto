# 设计说明：P0 Redis 基建与缓存分层基线

## 目标

本次设计的目标不是提前实现所有业务缓存，而是先定义一套后续能够稳定复用的 Redis 基建和缓存分层方式。

重点解决四件事：

1. `libs/cache` 到底负责什么
2. 业务缓存 key、TTL 和值结构应该放在哪里
3. 什么时候需要把缓存契约提取到 `packages/`
4. Redis key 应该如何命名，才能兼顾可读性、隔离性和未来演进

## 设计原则

- 基建与业务语义分层：`libs/cache` 负责基础设施和通用原语，业务模块负责自身缓存语义
- 先最小可复用，再逐步扩展：先满足验证码、冷却时间、频控计数等首批刚需，不在本次 change 中一次性塞入过多高级模式
- 跨运行时共享才提取契约：不是所有 key 都应放进 `packages/`
- 环境隔离和版本演进优先：key 设计从第一天就考虑环境和版本
- 敏感标识不裸奔：手机号、邮箱、证件号等不直接明文进入 Redis key
- 文档与注释同步交付：README、必要注释和入口文档属于正式交付内容

## 分层模型

推荐分为三层：

### 1. 共享运行时层：`libs/cache`

职责：

- Redis 连接与生命周期管理
- NestJS 可复用 `CacheModule`
- 通用 `RedisService`
- key namespace / key builder helper
- 通用缓存原语
  - JSON KV
  - counter
  - rate limit primitive

不负责：

- 某个业务模块的全部 key 常量集中管理
- 业务语义化 TTL 规则
- 多业务共享之外的契约定义

### 2. 业务本地缓存层：例如 `apps/api/src/modules/auth/cache/`

职责：

- 本业务自己的 key builder
- 本业务自己的 TTL 常量
- 本业务自己的 value schema
- 本业务围绕共享缓存原语的语义封装

例如未来 `auth` 可以定义：

- `authOtpCodeKey(phoneHash)`
- `authOtpCooldownKey(phoneHash)`
- `authOtpSendLimitKey(phoneHash)`
- `authLoginFailureKey(phoneHash)`

这样可以保证：

- key 的业务语义与使用场景留在本模块
- review 时变更范围更清晰
- 避免 `libs/cache` 演化成一个耦合所有业务的“全局 key 文件”

### 3. 跨运行时共享契约层：`packages/cache_contracts`

只有在多个运行时真正共享同一套 key 和 value schema 时，才提取到 `packages/cache_contracts`。

典型条件包括：

- `api` 和 `worker` 都需要读写同一类 key
- 同一套缓存值结构需要被多个运行时稳定解析
- 某类 key 已经形成明确版本化契约，而不是业务内部实现细节

在未满足上述条件前，不建议过早提取。

## Redis Key 命名规范

建议统一格式：

```txt
nenggan:{env}:{domain}:{version}:{resource}:{identifier}
```

说明：

- `env`
  - 例如 `dev`、`test`、`staging`、`prod`
- `domain`
  - 例如 `auth`、`chat`、`agents`
- `version`
  - 例如 `v1`
- `resource`
  - 例如 `otp-code`、`otp-cooldown`、`otp-send-limit`
- `identifier`
  - 对应具体实例标识，例如用户、手机号 hash、会话 id 等

`auth` 场景示例：

```txt
nenggan:dev:auth:v1:otp-code:{phoneHash}
nenggan:dev:auth:v1:otp-cooldown:{phoneHash}
nenggan:dev:auth:v1:otp-send-limit:{phoneHash}
nenggan:dev:auth:v1:login-failure:{phoneHash}
```

约束：

- 必须带 `env`，避免不同环境串值
- 必须带 `version`，为后续迁移预留空间
- 不应直接把手机号等敏感标识明文写入 key
- identifier 应优先使用标准化后再 hash 的结果
- 业务语义应体现在 `domain` 和 `resource` 上，不建议使用难懂缩写

## 首期建议的共享缓存原语

为了支撑后续 `auth` 及其他基础业务，首期建议 `libs/cache` 至少提供：

- `RedisService`
  - 暴露底层连接与基础操作
- `keyFactory` / `namespace helper`
  - 统一拼装带环境、领域和版本的 key
- JSON KV 原语
  - 支持 `set/get/delete` 与 TTL
- counter 原语
  - 支持按 key 递增并配置 TTL
- rate limit primitive
  - 基于 counter 和 TTL 封装基础频控能力

本次刻意不纳入：

- distributed lock
- pub/sub
- stream
- advanced cache invalidation
- queue abstraction

这些能力后续可以通过独立小 change 继续补齐。

## 未来 `auth` 的接入方式

本次 change 不直接实现 `auth`，但应为 `auth` 提供清晰接入面。

推荐未来目录：

```txt
apps/api/src/modules/auth/cache/
├─ auth-cache.keys.ts
├─ auth-cache.constants.ts
├─ auth-cache.types.ts
└─ auth-cache.service.ts
```

其中：

- `auth-cache.keys.ts`
  - 负责 auth 自己的 key builder
- `auth-cache.constants.ts`
  - 负责 auth 自己的 TTL 和频控窗口常量
- `auth-cache.types.ts`
  - 负责 auth 自己的缓存 value schema
- `auth-cache.service.ts`
  - 负责把 `libs/cache` 原语包装成 auth 自己可读的业务接口

这样后续 `auth` change 可以直接复用，而不需要重新争论 key 落位问题。

## README 与注释要求

本次 change 本身应同步补齐：

- `libs/cache/README.md`
  - 说明职责边界、公开入口、配置依赖、key 命名规范、提取条件
- 根 README 或相关入口文档
  - 如新增 Redis 相关环境变量、启动方式或开发者使用说明，应同步更新
- 必要代码注释
  - 对 key 规则、敏感标识 hash、TTL 语义、rate limit 边界等非直观逻辑给出必要说明

## 与后续 change 的关系

该 change 完成后，后续 change 应默认建立在这套 Redis 基建之上，例如：

- `auth` 重做中的验证码、冷却时间和频控
- 通知或调度相关的短期状态
- 未来 worker 与 API 之间真正需要共享的缓存契约

它们不再各自重新发明 Redis 接线与 key 归属规则，而是复用本次 change 提供的基础层和分层约束。
