# 设计说明：Public Content Step 12 Feed 与 Detail 契约回对齐

## 目标

本 step 的目标是让 public feed 与 public post detail 这两条读侧主线，在不破坏“公开可读”前提的情况下，能够对齐当前登录用户的最小互动状态，并修正当前读侧契约中的分页参数与时间字段漂移。

本 step 只解决三件事：

- public read endpoint 如何在“匿名可读”和“登录态增强”之间保持同一条受控路径
- content / feed 读侧的 `limit` 查询参数如何稳定完成数字化
- public post detail 的 `updatedAt` 如何回到真实字段语义

## 非目标

本 step 不承担以下内容：

- 为首页 feed 引入新的推荐排序、个性化召回或复杂用户画像
- 修复 likes / favorites / comments 对非公开对象的边界放行
- 改写 interaction summary 的聚合模型或新增行为信号类型

## 核心边界

### Optional Public Read Auth

负责：

- 对 public feed / public detail 尝试读取 `Authorization: Bearer ...`
- 在 header 缺失时保持匿名读取，不把公开接口强制升级为受保护接口
- 在 token 合法时把用户上下文挂到 request，供 summary projection 复用
- 在 token 明确存在但非法、过期或会话失效时返回稳定未授权结果，避免客户端静默降级成匿名态

它不负责新的 full access 判定，也不负责刷新 token。

### Interaction Summary Projection Wiring

负责：

- 将 optional auth 提供的 `userId` 透传到 feed/detail 读侧的 summary 查询
- 保持匿名调用时 `isLiked` / `isFavorited` 为 `null`
- 保持 summary 仍然由 interactions 模块聚合，不把判断责任散落到 controller 层

### Read Contract Normalization

负责：

- 在 DTO 层显式完成 `limit` 数字转换，而不是依赖隐式框架行为
- 让 public post detail 直接返回 repository 已读取到的真实 `updatedAt`
- 同步 Swagger / OpenAPI / 回归测试中的代表性契约表达

## 流程

```text
public feed / public detail 请求
            │
            ▼
  检查是否带 Authorization header
            │
      ┌─────┴─────────────┐
      │                   │
   未携带               已携带
      │                   │
      ▼                   ▼
  匿名读取          校验 token / session
      │                   │
      │             ┌─────┴──────────┐
      │             │                │
      │          校验通过         校验失败
      │             │                │
      │             ▼                ▼
      │       注入当前 user        返回 401
      │             │
      └───────┬─────┘
              ▼
     读取 feed / detail 主结果
              │
              ▼
    interaction summary 按是否有 userId
    决定是否补 isLiked / isFavorited
              │
              ▼
      返回对齐后的 DTO / OpenAPI 契约
```

## 与前后 step 的关系

- `step-02` 已提供 public post detail 的基础读取主线
- `step-04` 与 `step-06` 已提供首页 feed、分页与刷新边界
- `step-11` 已提供 interaction summary 聚合能力，但 controller 级接线仍未闭环
- 本 step 在不新增新能力主题的前提下，把这些既有读侧结果回对齐到可验收状态
