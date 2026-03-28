# 任务拆解：P0 可运行框架基线

## 1. Workspace 与根级入口

- [x] 确认 monorepo 根级 package manager / workspace 编排方案
- [x] 定义根级常用命令入口，覆盖安装、启动、停止、构建、验证等动作
- [x] 补齐根级 README 或等价文档中的最小启动说明

## 2. Docker Compose 本地依赖

- [x] 提供本地开发用 `docker compose` 配置，至少覆盖 PostgreSQL 与 Redis
- [x] 统一首期 compose 文件为 `infra/docker/compose.dev.yml`
- [x] 确认 compose 文件路径与命名规则
- [x] 确认容器启动后的最小可验证方式

## 3. Docker Compose 应用联动

- [x] 设计 compose profile，用于拉起 `api`、`admin-web`、`worker`
- [x] 确认这些应用在 compose 中的最小运行方式与依赖接线
- [x] 确认保留本机直跑路径，不强制所有开发都依赖 compose

## 4. 开发脚本

- [x] 新增 `infra/scripts/dev-up.sh`
- [x] 新增 `infra/scripts/dev-down.sh`
- [x] 新增 `infra/scripts/dev-reset.sh`
- [x] 新增 `infra/scripts/dev-stack.sh`
- [x] 新增 `infra/scripts/openapi-export.sh`
- [x] 新增 `infra/scripts/health-check.sh`
- [x] 在根级 `package.json` 中暴露 `dev-up`
- [x] 在根级 `package.json` 中暴露 `dev-down`
- [x] 在根级 `package.json` 中暴露 `dev-reset`
- [x] 在根级 `package.json` 中暴露 `dev-stack`
- [x] 在根级 `package.json` 中暴露 `dev-api`
- [x] 在根级 `package.json` 中暴露 `dev-admin`
- [x] 在根级 `package.json` 中暴露 `dev-worker`
- [x] 在根级 `package.json` 中暴露 `dev-mobile`
- [x] 在根级 `package.json` 中暴露 `openapi-export`
- [x] 在根级 `package.json` 中暴露 `health-check`
- [x] 确认不使用 Windows 专用脚本作为标准开发脚本入口

## 5. 应用最小壳

- [x] 让 `apps/api` 能启动并提供 `/health` 或等价存活结果
- [x] 让 `apps/worker` 能启动并验证基础依赖连接
- [x] 让 `apps/admin-web` 能启动空壳页面
- [x] 让 `apps/mobile` 能启动空壳应用

## 6. 环境与配置

- [x] 提供 `.env.example` 或等价环境变量样板
- [x] 确认本地环境变量与 compose 依赖的最小接线
- [x] 确认 Prisma 与本地数据库的最小初始化路径

## 7. 验证与验收

- [x] 验证开发者可通过单一入口完成初始化
- [x] 验证可通过 `docker compose` 一键拉起本地依赖
- [x] 验证可通过 compose profile 一键拉起 `api`、`admin-web`、`worker`
- [x] 验证 `.sh` 脚本可在 Ubuntu 环境直接运行
- [x] 验证 `dev-up`、`dev-down`、`dev-reset`、`dev-stack` 命令可执行
- [x] 验证 `openapi-export` 与 `health-check` 命令可执行
- [x] 验证 API、worker、admin-web、mobile 可分别启动最小壳
- [x] 验证 OpenAPI 导出与共享契约生成存在明确入口
