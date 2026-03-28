# 任务拆解：P0 Prisma 与数据库初始化

## 1. 依赖与命令入口

- [x] 确认 `prisma` CLI 与 `@prisma/client` 的首期安装位置
- [x] 确认根级数据库命令入口：`db-generate`、`db-migrate`、`db-reset`
- [x] 评估是否在首期同步提供 `db-studio` 入口

## 2. Prisma 真相源初始化

- [x] 在根目录创建 `prisma/schema.prisma`
- [x] 建立 `prisma/migrations/` 的首期使用约定
- [x] 确认是否为首期预留 `seed` 入口与目录结构

## 3. 运行时数据库封装

- [x] 创建 `libs/database` 的最小包结构或模块壳
- [x] 明确 `PrismaClient`、数据库模块与事务封装的统一落位
- [x] 明确 `apps/api` 与 `apps/worker` 通过 `libs/database` 接入数据库的方式

## 4. 环境变量与本地初始化流程

- [x] 在根级环境示例中加入 `DATABASE_URL`
- [x] 验证本地 PostgreSQL 与 Prisma 初始化命令的连接关系
- [x] 固化首期本地初始化顺序：`dev-up` -> `db-generate` -> `db-migrate`

## 5. 验证与验收

- [x] 验证 Ubuntu 环境下 Prisma generate 与 migration 可以正常执行
- [x] 验证 `apps/api` 与 `apps/worker` 不会各自维护独立 schema 真相源
- [x] 验证数据库初始化说明足以支撑 `p0-auth-sms-login` 进入实现阶段
