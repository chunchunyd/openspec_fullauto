# Delta for Cache

## ADDED Requirements

### Requirement: 系统必须提供统一 Redis 共享运行时接入层

系统必须提供统一的 Redis 共享运行时接入层，供后续业务模块复用，而不是由各业务模块分别创建原生 Redis 接线。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期该共享层至少应包括：

- 可复用的 `CacheModule`
- Redis 生命周期管理
- 面向业务模块的基础访问入口


#### Scenario: API 复用共享 Redis 接入层

- WHEN `apps/api` 中的业务模块需要访问 Redis
- THEN 它必须通过 `libs/cache` 提供的共享运行时接入层完成接线
- AND 不应在业务模块中长期复制一套独立 Redis client 初始化逻辑

#### Scenario: Worker 复用共享 Redis 接入层

- WHEN `apps/worker` 中的处理器或调度逻辑需要访问 Redis
- THEN 它必须优先通过 `libs/cache` 提供的共享运行时接入层完成接线
- AND 不应在 worker 内部单独维护另一套长期独立的基础接线层

### Requirement: 系统必须统一 Redis 键命名规范

系统必须对 Redis 键采用统一的命名规范，以支持环境隔离、领域分层和后续版本演进。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

键名至少应表达以下维度：

- 环境
- 领域
- 版本
- 资源语义
- 标识符


#### Scenario: 生成业务缓存键

- WHEN 业务模块需要生成 Redis key
- THEN key 必须遵循统一命名规范
- AND key 不应缺失环境或版本信息

#### Scenario: 处理敏感标识

- WHEN 业务缓存键使用手机号、邮箱或其他敏感标识作为定位依据
- THEN 系统不得直接将这些敏感标识明文放入 Redis key
- AND 系统应优先使用标准化后的 hash 或等价脱敏标识

### Requirement: 系统必须提供首期共享缓存原语

系统必须提供首期共享缓存原语，以支撑短期状态、计数器和基础频控场景。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- JSON KV 存取
- TTL 控制
- 计数器
- 基础 rate limit primitive


#### Scenario: 存储短期 JSON 状态

- WHEN 业务模块需要缓存带 TTL 的短期状态
- THEN 共享缓存层必须支持以统一方式读写 JSON 值
- AND 该值必须能够配置有效期

#### Scenario: 进行基础频控

- WHEN 业务模块需要对发送验证码、登录失败等行为做基础频控
- THEN 共享缓存层必须提供可复用的计数或频控原语
- AND 业务模块不应各自重复实现底层计数与过期逻辑

### Requirement: 系统必须保留业务缓存语义的本地 ownership

系统必须将业务缓存语义保留在业务模块自身，而不是将所有业务缓存规则上收至共享缓存基础层。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

业务缓存语义至少包括：

- 业务 key builder
- 业务 TTL 常量
- 业务 value schema
- 业务层围绕共享缓存原语的语义封装


#### Scenario: Auth 定义验证码缓存语义

- WHEN `auth` 模块需要定义验证码、冷却时间或频控相关缓存
- THEN 这些业务语义必须保留在 `auth` 模块自身的缓存目录中
- AND `libs/cache` 只负责共享运行时与通用原语

#### Scenario: 后续能力定义业务缓存语义

- WHEN 其他业务能力需要建立自己的缓存规则
- THEN 它们应在各自模块内定义相应缓存语义
- AND 不应把本应属于业务模块的具体 key 常量全部集中堆入共享基础层

### Requirement: 系统必须在跨运行时共享时提取缓存契约

系统必须在多个运行时真正共享同一套缓存 key 与值结构时，提取共享缓存契约，而不是继续依赖多份本地副本。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: API 与 worker 共享同一套缓存契约

- WHEN `api` 与 `worker` 需要共同读写同一套缓存 key 与值结构
- THEN 系统必须将这套共享契约提取到 `packages/cache_contracts` 或等价共享契约包
- AND 两侧实现必须共同依赖这份共享契约，而不是各自维护本地副本
