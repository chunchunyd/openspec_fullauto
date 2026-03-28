# 变更提案：Mobile Foundation Step 02 HTTP 契约与请求管线

## 为什么要做

在 app shell 入口边界建立之后，mobile 端接下来最需要的不是具体 auth 页面，而是统一的 API 接入边界。

如果没有这一层：

- 各 feature 会各自维护 base URL、header、超时与错误分支
- mobile 很容易重新回到口头约定字段或手写漂移 DTO
- 后续 auth、内容、设置等模块会在最底层 transport 上重复造轮子

同时，当前项目已经明确要求前端以共享 OpenAPI 产物作为 HTTP contract 依据，因此需要先把 contract 消费与 request pipeline 单独收敛出来。

## 本次变更包含什么

本次变更聚焦移动端 HTTP 契约与请求管线，范围包括：

- 以 `packages/api_contracts/openapi/openapi.json` 作为 mobile 的共享 contract 基线
- 为 mobile 建立统一的 API client 入口与请求管线
- 建立环境相关的 base URL、header 与 timeout 装配边界
- 建立网络错误、超时、4xx、5xx 的最小错误映射

## 本次变更不包含什么

本次变更不包含以下内容：

- 手机号输入页或验证码页
- refresh token 流程
- 本地会话持久化
- 页面级 loading / empty / retry 组件
- 具体 analytics 事件上报 SDK

## 预期结果

完成后，项目应具备以下结果：

1. mobile 端有统一的 API client 入口，而不是页面各自直连底层 HTTP 库
2. mobile 端以共享 OpenAPI 产物为字段依据，而不是长期依赖口头约定
3. base URL、header、timeout 与基础错误映射有明确 owner
4. 后续 auth 与其他 feature 可以复用同一请求管线

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/core/network`
- `apps/mobile/lib/app/env`
- `packages/api_contracts/openapi/openapi.json` 的消费方式
- `apps/mobile/README.md`
