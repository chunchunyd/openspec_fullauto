# Runtime Config Specification

## Purpose

本规格定义“能干”项目当前服务端运行时配置加载与数据库连接字符串校验的行为真相源。

首期 runtime config 能力聚焦于：

- `apps/api` 与 `apps/worker` 启动时显式完成环境加载
- monorepo 根目录 `.env` 作为本地开发默认配置来源
- `DATABASE_URL` 在启动阶段完成最小规范化与显式校验

## Requirements

### Requirement: 服务端运行时必须显式完成本地环境加载

系统必须在 `apps/api` 与 `apps/worker` 启动时，先完成运行时环境变量加载，再初始化数据库、缓存、队列等基础设施依赖。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

本地开发默认环境来源应为 monorepo 根目录 `.env` 或等价显式配置来源。


#### Scenario: 从子应用目录启动本地服务

- WHEN 贡献者通过仓库标准命令启动 `apps/api` 或 `apps/worker`
- THEN 运行时必须能够发现并加载 monorepo 根目录的 `.env`
- AND 不应要求贡献者额外手工 export `DATABASE_URL` 才能完成最小本地启动

#### Scenario: 部署环境已显式注入变量

- WHEN 运行时所在环境已经显式注入 `DATABASE_URL` 等关键变量
- THEN 这些显式注入值必须优先于本地 `.env`
- AND 本地开发用 `.env` 不得错误覆盖部署环境配置

### Requirement: 数据库运行时配置必须失败快速并给出明确错误

系统必须在构造 Prisma / PostgreSQL 运行时连接前，对 `DATABASE_URL` 进行最小规范化与显式校验。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

当配置无效时，系统必须在启动阶段抛出明确配置错误，而不是等到 readiness 或业务请求阶段才暴露底层驱动报错。


#### Scenario: 缺失数据库连接字符串

- WHEN `DATABASE_URL` 缺失、为空值或仅包含空白字符
- THEN 应用必须在启动阶段失败
- AND 错误信息必须明确指出 `DATABASE_URL` 配置无效

#### Scenario: 连接字符串带包裹引号

- WHEN `DATABASE_URL` 来自常见 `.env` 写法并带有外层单引号或双引号
- THEN 系统必须在构造连接前去除外层包裹字符
- AND 不应因为该类可规范化输入而落入底层驱动的认证类型错误

#### Scenario: 非法协议或明显不可解析的连接字符串

- WHEN `DATABASE_URL` 不符合 PostgreSQL 连接字符串的最小格式要求
- THEN 应用必须在启动阶段失败
- AND 不应在 `/health/ready` 首次访问时才暴露底层连接异常
