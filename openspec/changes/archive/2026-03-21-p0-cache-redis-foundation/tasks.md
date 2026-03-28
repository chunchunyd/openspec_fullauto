# 任务拆解：P0 Redis 基建与缓存分层基线

## 1. 契约与规格

- [x] 为 `cache` capability 建立本次 change 的 spec delta
- [x] 为 `repository-structure` 建立本次 change 的 spec delta，明确 key 归属与共享契约提取规则
- [x] 在 proposal/design 中确认：`libs/cache`、业务模块本地缓存目录、`packages/cache_contracts` 三层职责边界
## 2. `libs/cache` 共享运行时基础层
- [x] 创建 `libs/cache` 的可复用包结构与公开入口
- [x] 补齐 `CacheModule` 与 `RedisService` 的最小运行时接线
- [x] 约定 Redis 配置读取方式、生命周期管理和错误处理策略
- [x] 明确不在本 change 中接入 queue、pub/sub、lock 等高级模式
## 3. Key 规范与共享原语
- [x] 实现统一的 key namespace / key factory 辅助能力
- [x] 固化 `nenggan:{env}:{domain}:{version}:{resource}:{identifier}` 这类 key 设计规范
- [x] 明确敏感标识的标准化与 hash 规则，不直接在 key 中写入手机号等明文
- [x] 提供 JSON KV 原语与 TTL 支持
- [x] 提供 counter 原语与 TTL 支持
- [x] 提供基础 rate limit primitive，供后续 `auth` 等模块复用
## 4. 业务接入边界与未来提取规则
- [x] 补充示例或文档，说明业务 key、TTL 和 value schema 应优先放在模块自己的 `cache/` 目录下
- [x] 明确何时应从业务模块提取到 `packages/cache_contracts`
- [x] 确认在当前阶段不把所有业务 key 收口到 `libs/cache`
- [x] 确认后续 `auth` change 只需要建立模块内缓存目录并复用 `libs/cache`，不再重复造 Redis 基建
## 5. 文档、注释与入口说明
- [x] 编写或更新 `libs/cache/README.md`
- [x] 如 Redis 启动方式、环境变量或开发入口发生变化，更新根 README 或相关入口文档
- [x] 对 key 规范、hash 规则、TTL 语义和提取条件补充必要注释或模块说明
## 6. 验证与验收
- [x] 为 key factory、namespace helper、JSON KV、counter 与 rate limit primitive 补单元测试
- [x] 验证本地 Redis 环境下的基本连接、TTL、计数和序列化行为
- [x] 验证消费方可以通过 `libs/cache` 复用 Redis 能力，而不是直接创建原生 client
- [x] 验证文档足以支撑后续 `auth` change 接入 Redis 基建
