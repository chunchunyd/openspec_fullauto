# 变更提案：Public Content Step 02 公开帖子详情读取模型

## 为什么要做

当前 `content` 已经有写入主线和最小公开列表入口，但还缺少正式的公开帖子详情读取边界。没有详情模型，feed 卡片、互动入口和后续治理链路都无法围绕同一个帖子详情主线协作。

## 本次变更包含什么

- 建立公开帖子详情读取接口与最小 service/repository 读取主线
- 返回帖子主体、作者 Agent 公开摘要、来源标识和 AI 标识
- 严格限制非公开状态或非公开作者的帖子详情访问

## 本次变更不包含什么

- feed 首页聚合与排序
- 点赞、评论、收藏、举报等互动写入
- 管理端审核与下线操作

## 预期结果

1. 客户端可以围绕公开帖子详情建立统一读取主线。
2. 非公开内容不会被误当作正常公开详情返回。
3. 后续互动与 feed 详情跳转有明确的数据锚点。

## 影响范围

- `apps/api/src/modules/content/*`
- `apps/api/src/modules/content/__tests__/*`
- `packages/api_contracts/openapi/openapi.json`

