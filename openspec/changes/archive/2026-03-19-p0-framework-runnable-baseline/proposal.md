# 变更提案：P0 可运行框架基线

## 为什么要做

在进入 `p0-auth-sms-login` 之前，项目需要先具备一个“可运行、可联调、可验证”的工程基线。

如果 monorepo 目录只是结构设计而没有最小运行能力，后续业务 change 会同时混入工程初始化、环境配置、依赖编排和本地联调问题，导致：

- 业务 change 范围过大
- 本地启动方式不统一
- API、worker、admin-web、mobile 的接线方式漂移
- 新同学或多 Agent 协作无法快速进入工作状态

因此需要在 P0 业务能力之前，先建立一个可运行框架基线。

## 本次变更包含什么

本次变更聚焦于“框架先跑起来”，范围包括：

- monorepo 根级 workspace 任务入口
- `apps/api`、`apps/admin-web`、`apps/worker`、`apps/mobile` 的最小可运行壳
- 本地依赖的 `docker compose` 一键启动方式
- 通过 `docker compose` profile 一键拉起 `api`、`admin-web`、`worker` 的本地全栈能力
- 本地开发常用脚本
- 基础环境变量样板
- 最小 health / readiness 验证路径
- OpenAPI 导出与共享契约生成的基础命令入口

## 本次变更不包含什么

本次变更不包含以下内容：

- 短信登录、Agent、聊天、内容流等具体业务闭环
- 完整生产级部署体系
- 复杂 CI/CD 流水线
- 完整监控平台接入
- 所有业务表与完整数据库模型

## 预期结果

完成后，项目应满足以下最小工程目标：

1. 一名开发者拉取仓库后能按统一入口完成初始化
2. 能通过 `docker compose` 一键拉起本地依赖
3. 能通过统一脚本或 compose profile 启动 API、admin-web、worker 的最小壳
4. `mobile` 能通过本机开发方式启动最小壳
5. API 与 worker 至少有基础健康检查或等价可验证运行结果
6. OpenAPI 导出和共享契约生成具备可执行入口

## 影响范围

本次变更主要影响：

- `repository-structure` capability
- monorepo 根目录脚本与 workspace 编排
- `infra/` 中本地开发依赖与 compose 配置
- `tools/` 中导出和初始化相关脚本
- `apps/api`、`apps/admin-web`、`apps/worker`、`apps/mobile` 的最小运行壳
