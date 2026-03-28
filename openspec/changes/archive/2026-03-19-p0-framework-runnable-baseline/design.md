# 设计说明：P0 可运行框架基线

## 目标

本次设计的目标不是搭完整业务系统，而是定义一个统一、低摩擦的本地开发启动面。

重点解决三件事：

1. 本地依赖如何启动
2. 各应用如何通过统一入口启动
3. 启动后如何快速验证“框架是活的”

## 设计原则

- 一键优先：本地依赖必须支持 `docker compose` 一键拉起
- 脚本收口：常见动作必须通过根级脚本或 workspace 命令触发，而不是让开发者手敲分散命令
- 先最小可运行，再逐步加业务：每个 app 先有最小壳和健康结果，不在此 change 中混入业务逻辑
- 与 monorepo 结构一致：运行入口服从 `apps/*`、`infra/`、`tools/`、`prisma/` 的既有边界
- 保留双路径：支持 compose 全栈拉起，也保留本机直跑作为开发补充方式

## 本地依赖拓扑

首期本地依赖建议至少包括：

- PostgreSQL
- Redis

这些依赖应通过 `docker compose` 启动，后续如需对象存储 mock、消息队列或观测组件，可在不破坏主入口的前提下扩展。

建议提供统一入口，例如：

- `docker compose -f infra/docker/compose.dev.yml up -d`

并在根级脚本中进一步收口为更直观的命令，例如：

- `dev-up`
- `dev-down`
- `dev-reset`

建议首期先统一使用一个 compose 文件：

- `infra/docker/compose.dev.yml`

在这个文件中：

- 默认服务负责本地基础依赖
- `api`、`admin-web`、`worker` 通过 profile 或等价机制按需启用

## 应用容器化策略

除基础依赖外，首期建议支持通过 `docker compose` profile 拉起以下本地应用：

- `api`
- `admin-web`
- `worker`

这样可以满足：

- 新开发者快速得到全栈本地环境
- 本地 smoke 验证更接近统一环境
- API、后台和 worker 在本地联调时减少手工启动步骤

同时，系统仍应保留本机直接运行这些应用的方式，避免强制所有开发场景都依赖容器化。

对于 `mobile`：

- 首期仍以本机 `flutter run`、模拟器或真机调试为优先路径
- 不要求将 Flutter App 本身作为 compose 默认运行单元
- 但可以在文档中说明其与本地 API / admin / worker 的联调方式

## 推荐脚本命名

为了减少后续实现时的命名分歧，首期建议优先采用以下根级脚本名：

- `dev-up`
  - 启动本地基础依赖
- `dev-down`
  - 停止本地基础依赖
- `dev-reset`
  - 清理并重建本地依赖环境
- `dev-stack`
  - 通过 compose profile 拉起 `api`、`admin-web`、`worker`
- `dev-api`
  - 本机直跑 API
- `dev-admin`
  - 本机直跑 admin-web
- `dev-worker`
  - 本机直跑 worker
- `dev-mobile`
  - 本机直跑 Flutter mobile
- `openapi-export`
  - 导出 OpenAPI 文档与共享契约产物
- `health-check`
  - 执行基础健康检查或 smoke 验证

这些名称可以映射到 package scripts、`bash/sh` 脚本或其他 workspace 命令，但对开发者暴露的名字建议保持一致。
考虑到项目后续主要在 Ubuntu 环境开发，首期不应将 `.ps1` 作为标准脚本入口。

## 根级脚本约定

首期建议最少提供以下脚本能力：

- 初始化依赖
- 启动本地依赖
- 关闭本地依赖
- 通过 compose profile 启动本地全栈应用
- 启动 API
- 启动 admin-web
- 启动 worker
- 启动 mobile
- 导出 OpenAPI
- 执行基础健康检查或 smoke 验证

脚本可以通过 workspace 命令、`bash/sh` 或等价机制实现，但对开发者暴露的入口必须统一、稳定、可文档化。

## 首批建议文件清单

为了让本次 change 更容易直接落地，首批建议明确以下实际文件：

- `infra/docker/compose.dev.yml`
- `infra/scripts/dev-up.sh`
- `infra/scripts/dev-down.sh`
- `infra/scripts/dev-reset.sh`
- `infra/scripts/dev-stack.sh`
- `infra/scripts/openapi-export.sh`
- `infra/scripts/health-check.sh`
- 根级 `package.json`
- 根级 `.env.example`
- `apps/api` 中的最小 health 入口实现文件

建议映射关系如下：

- `dev-up` -> 调用 `infra/scripts/dev-up.sh`
- `dev-down` -> 调用 `infra/scripts/dev-down.sh`
- `dev-reset` -> 调用 `infra/scripts/dev-reset.sh`
- `dev-stack` -> 调用 `infra/scripts/dev-stack.sh`
- `openapi-export` -> 调用 `infra/scripts/openapi-export.sh`
- `health-check` -> 调用 `infra/scripts/health-check.sh`

其中：

- 根级 `package.json` 负责暴露统一命令名
- `infra/scripts/*.sh` 负责具体执行逻辑
- Ubuntu 作为主要开发环境时，应默认保证这些 `.sh` 脚本可直接运行

## 健康检查与导出入口

首期建议先约定以下最小验证目标：

- `apps/api` 至少暴露 `/health` 或等价健康接口
- `apps/worker` 至少能通过脚本验证其进程存活和基础依赖连接
- `health-check` 脚本至少检查：
  - API 健康状态
  - 数据库依赖是否可连通
  - Redis 依赖是否可连通

OpenAPI 导出建议统一收口到：

- 根级 `openapi-export` 脚本
- 输出位置优先写入 `docs/api/` 或 `packages/api_contracts/` 的既定链路

## 可运行结果定义

本次 change 完成时，各应用的最小可运行结果应为：

- `apps/api`：能启动并返回 health 或等价存活结果
- `apps/worker`：能启动并完成基础依赖连接或等价存活结果
- `apps/admin-web`：能启动空壳管理界面
- `apps/mobile`：能启动空壳应用或基础路由页

这类最小壳不要求具备业务闭环，但必须可证明框架接线正确。

额外要求：

- `api`、`worker`、`admin-web` 应支持 compose profile 方式的一键联动启动
- `mobile` 应保留本机启动优先路径

## 与后续业务 change 的关系

该 change 完成后，后续业务 change 默认建立在此基线之上：

- `p0-auth-sms-login`
- 未来的 `feed`、`chat`、`agent-publication` 等 change

它们不再重复定义“本地怎么启动”，而是直接复用这次 change 提供的统一运行面。
