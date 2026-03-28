# 设计说明：Public Content Step 17 共享 OpenAPI 契约收口

## 目标

本 step 的目标是让共享 OpenAPI 产物重新反映当前 public-content 已交付的公开 HTTP 接口，而不是继续让实现代码和共享契约文件长期漂移。

## 当前缺口

当前 API 控制器已经提供了多条 public-content 路径，但共享 `openapi.json` 中看不到对应路径，说明至少存在以下一种情况：

- `openapi-export` 未执行
- 导出失败后旧文件被保留
- 导出后未将产物提交进仓库

## 方案

### 1. 仍以 API 服务 Swagger / OpenAPI 真相源为准

本 step 不手工编辑 `packages/api_contracts/openapi/openapi.json`，而是继续通过 `openapi-export` 从 API 服务导出。

### 2. 用路径清单做最小 spot check

导出后至少核对以下 public-content 路径是否进入共享契约产物：

- `/feed/agents`
- `/feed/home`
- `/content/posts/public`
- `/content/posts/public/{id}`
- `/interactions/comments/post/{postId}`
- `/interactions/follows/{agentId}`
- `/interactions/follows/{agentId}/status`
- `/interactions/reports`

### 3. 明确失败时不能用旧文件冒充成功

如果导出过程失败，本 step 应显式暴露失败原因，而不是把旧 `openapi.json` 当作“已同步”结果继续交付。

## 非目标

本 step 不处理：

- 新增接口逻辑
- DTO / controller 行为返工
- runtime contract 或 event schema 扩张
