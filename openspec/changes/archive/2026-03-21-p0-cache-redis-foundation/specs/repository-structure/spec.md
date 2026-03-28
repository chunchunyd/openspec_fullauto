# Delta for Repository Structure

## ADDED Requirements

### Requirement: 仓库必须分层管理缓存键定义与缓存契约

系统必须将 Redis 共享运行时基础设施、业务模块本地缓存键定义和跨运行时缓存契约分层管理，而不是全部堆在单一共享目录中。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

其中：

- `libs/cache` 负责 Redis 连接、共享运行时封装、key namespace helper 和通用缓存原语
- 业务模块负责自身 key builder、TTL 常量和值结构
- 只有在多个运行时真正共享同一套 key 与值结构时，才应提取到 `packages/cache_contracts` 或等价共享契约包


#### Scenario: 单一业务模块定义自身缓存键

- WHEN `auth` 等单一业务模块定义自己的验证码、冷却时间或频控缓存键
- THEN 这些 key builder、TTL 和 value schema 应放在该业务模块自己的 `cache/` 目录中维护
- AND `libs/cache` 不应演化成收口全部业务 key 的全局目录

#### Scenario: 跨运行时共享缓存契约

- WHEN `api`、`worker` 或多个运行时需要共享同一套缓存 key 与值结构
- THEN 这些共享契约必须提取到 `packages/cache_contracts` 或等价共享契约包中维护
- AND 不得长期保留多份彼此漂移的模块内副本
