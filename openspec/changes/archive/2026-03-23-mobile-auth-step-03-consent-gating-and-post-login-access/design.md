# 设计说明：Mobile Auth Step 03 协议确认 gating 与登录后放行

## 目标

本 step 的目标是把“已登录但还不能放行完整产品”的状态，从临时 pending 边界升级为真实可操作的 mobile 协议确认流。

本 step 只解决三个问题：

- 当前 session 是否已经满足完整产品访问条件，由谁判定
- 未满足条件时 mobile 路由该如何分流
- 用户完成协议确认后，如何切换到完整产品空间

## 非目标

本 step 不承担以下内容：

- access token 失效后的自动 refresh
- 设备会话管理或当前设备 logout
- 协议正文 CMS 或版本管理后台

## 状态模型

本 step 不修改 foundation `AuthStateOwner` 的“是否存在可用 session”语义，而是在其之上增加一个受控 access gate 层：

- `session signed out`
- `session signed in + gated`
- `session signed in + full access`

这样可以保持 foundation 原语继续只负责 session，而把“是否可进入完整产品”留在 auth feature 层处理。

## 核心流程

```text
启动恢复 / 登录成功
        │
        ▼
确认存在可用 session
        │
        ▼
GET /auth/consent/status
        │
   ┌────┴───────────────────┐
   │                        │
可完整访问               仍缺必要确认
   │                        │
   ▼                        ▼
进入 full access          进入 consent gate
                              │
                              ▼
                    POST /auth/consent/record-all
                              │
                              ▼
                      gating 通过后放行
```

## 路由边界

- `auth` 空间：未登录用户的登录入口
- `gated` 空间：已登录但未完成协议确认的受控边界
- `protected/full access` 空间：已登录且已完成协议确认的完整产品空间

本 step 的关键不是多加一个页面，而是把这三种边界稳定下来，避免后续 feature 各自绕开 gating。

## 失败场景

### 获取 gating 状态失败

- 优先展示受控错误与重试入口
- 不得因为拉取失败而默认放行进入完整产品

### 记录协议部分失败

- 保持用户停留在 consent gate
- 展示哪些协议尚未完成
- 不得把“部分成功”错误地当作完整放行

## 与后续 step 的关系

- `step-02` 建立可恢复 session 与临时 gated pending 边界
- 本 step 把 pending 边界补成正式协议确认流
- `step-04` 会在当前已登录请求链路上继续补 refresh 与 401 恢复
