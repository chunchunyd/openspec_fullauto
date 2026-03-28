# Delta for Repository Structure

## ADDED Requirements

### Requirement: 仓库必须支持本地依赖的一键启动

系统必须为本地开发依赖提供 `docker compose` 一键启动能力。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期本地依赖至少应覆盖：

- PostgreSQL
- Redis


#### Scenario: 一键拉起本地依赖

- WHEN 开发者需要启动本地开发依赖
- THEN 仓库必须提供可文档化、可重复执行的 `docker compose` 启动入口
- AND 开发者不应需要手动分别初始化数据库和缓存服务

#### Scenario: 一键关闭本地依赖

- WHEN 开发者结束本地开发或需要停止依赖
- THEN 仓库必须提供对应的 compose 关闭入口

### Requirement: 仓库应支持通过 compose profile 拉起本地全栈应用

系统应支持通过 `docker compose` profile 或等价机制，一键拉起本地全栈中的核心 Web/服务端应用。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期推荐覆盖：

- `apps/api`
- `apps/admin-web`
- `apps/worker`


#### Scenario: 一键拉起本地全栈应用

- WHEN 开发者需要快速获得本地联调环境
- THEN 仓库应支持通过 compose profile 拉起 `api`、`admin-web`、`worker`
- AND 这些应用应能与 compose 启动的本地依赖协同工作

#### Scenario: 保留本机直跑路径

- WHEN 开发者不希望通过容器运行本地应用
- THEN 仓库仍应保留本机直接运行这些应用的方式
- AND compose 全栈方式不应成为唯一开发路径

### Requirement: 仓库必须为常见开发动作提供根级脚本入口

系统必须为本地开发常见动作提供统一的根级脚本或 workspace 命令入口。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期至少应覆盖：

- 初始化依赖
- 启动本地依赖
- 关闭本地依赖
- 通过 compose profile 启动本地全栈应用
- 启动 API
- 启动 admin-web
- 启动 worker
- 启动 mobile
- 导出 OpenAPI
- 基础健康检查或 smoke 验证


#### Scenario: 开发者执行常见动作

- WHEN 开发者需要完成本地初始化、启动或验证
- THEN 仓库必须提供统一入口
- AND 不得要求开发者在多个子项目中自行拼接零散命令

### Requirement: 仓库必须提供最小可运行应用壳

系统必须在进入首批业务 change 前，为核心应用提供最小可运行壳。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期最小可运行壳至少包括：

- `apps/api`
- `apps/admin-web`
- `apps/worker`
- `apps/mobile`


#### Scenario: 启动 API 最小壳

- WHEN 开发者启动 `apps/api`
- THEN 系统必须能够返回 health 或等价存活结果

#### Scenario: 启动 worker 最小壳

- WHEN 开发者启动 `apps/worker`
- THEN 系统必须能够验证其基础运行状态或依赖连接状态

#### Scenario: 启动前端最小壳

- WHEN 开发者启动 `apps/admin-web` 或 `apps/mobile`
- THEN 系统必须能够展示可验证的最小空壳结果

#### Scenario: mobile 启动方式

- WHEN 开发者启动 `apps/mobile`
- THEN 系统应优先支持本机 Flutter 开发方式
- AND 仓库不得强制要求 `mobile` 通过 compose 作为唯一运行方式
