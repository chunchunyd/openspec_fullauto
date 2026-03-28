# 变更提案：P0 Prisma 与数据库初始化

## 为什么要做

`p0-framework-runnable-baseline` 已经解决了本地运行框架与基础依赖启动的问题，但首期业务能力仍然缺少统一的数据层初始化基线。

如果没有一套明确的 Prisma 安装位置、数据库初始化顺序、迁移方式和运行时接入规则，后续以下能力都会在实现阶段反复分叉：

- `auth` 的用户、会话与协议确认持久化
- `agents` 的基础资料、配置与记忆存储
- `content` 与 `feed` 的内容模型沉淀
- `admin`、`analytics` 与 `moderation` 的最小留痕

当前 `repository-structure` 真相源已经定义了 `prisma/` 与 `libs/database` 的职责边界，但还没有形成一个面向实际初始化的独立 change。

## 本次变更包含什么

本次变更聚焦于首期数据库与 Prisma 初始化基线，范围包括：

- 明确 Prisma CLI 与相关依赖的安装位置
- 在根目录建立 `prisma/` 作为关系型 schema 真相源
- 约定本地开发使用的 `DATABASE_URL` 与基础环境变量
- 约定首期数据库命令入口，如 `db-generate`、`db-migrate`、`db-reset`
- 明确 `libs/database` 作为运行时数据库封装层的落位与接入方式
- 定义本地 PostgreSQL 已启动后的最小初始化顺序

## 本次变更不包含什么

本次变更不包含以下内容：

- 完整业务表结构设计
- 复杂 seed 数据与演示数据体系
- 读写分离、分库分表、多租户等高级数据库架构
- 生产环境备份、恢复与容灾流程
- 数据仓库、OLAP 或离线分析链路

## 预期结果

完成后，团队应能以统一方式完成首期数据库初始化：

1. 本地通过 `docker compose` 启动 PostgreSQL
2. 贡献者配置 `.env` 中的 `DATABASE_URL`
3. 贡献者通过统一命令完成 Prisma generate 与 migration
4. `apps/api` 与 `apps/worker` 通过 `libs/database` 访问同一套数据库运行时封装

## 影响范围

本次变更主要影响：

- `repository-structure` 中与 `prisma/`、`libs/database`、脚本入口相关的约束
- 首期本地开发初始化流程
- `auth` 等后续需要关系型持久化的 capability
