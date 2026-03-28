# Delta for Repository Structure

## ADDED Requirements

### Requirement: 仓库必须为 Prisma 初始化提供统一命令入口

系统必须为首期关系型数据库初始化提供统一、可重复执行的命令入口。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.

首期标准命令至少应包括：

- `db-generate`
- `db-migrate`
- `db-reset`

如团队需要调试数据库模型，可以额外提供 `db-studio`，但不得替代标准初始化命令。


#### Scenario: 初始化本地数据库

- WHEN 开发者已经通过 `docker compose` 启动本地 PostgreSQL
- THEN 开发者必须能够从仓库根级入口执行 Prisma generate 与 migration
- AND 初始化流程不得要求开发者在多个子包之间自行猜测命令位置

#### Scenario: 迭代数据库结构

- WHEN 贡献者修改关系型 schema
- THEN 贡献者必须沿用同一套根级数据库命令更新生成产物与 migration
- AND 不得通过手工修改派生产物替代正式的 Prisma 生成流程

### Requirement: 仓库必须为运行时数据库访问提供统一封装层

系统必须将 `libs/database` 作为首期运行时数据库访问封装层，并要求应用运行时通过该封装层接入数据库。 The system MUST satisfy the behavior, scope, and constraints described in this requirement.


#### Scenario: API 访问数据库

- WHEN `apps/api` 需要访问关系型数据库
- THEN 它必须通过 `libs/database` 提供的统一封装接入
- AND 不应在应用目录内单独复制 Prisma runtime 接线逻辑

#### Scenario: Worker 访问数据库

- WHEN `apps/worker` 需要访问关系型数据库
- THEN 它必须复用 `libs/database` 提供的统一封装
- AND 不应在 worker 内部维护另一套独立数据库接线层
