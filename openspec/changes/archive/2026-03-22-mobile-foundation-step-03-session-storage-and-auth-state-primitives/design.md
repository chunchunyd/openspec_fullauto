# 设计说明：Mobile Foundation Step 03 会话存储与认证状态原语

## 目标

本 step 的目标是在 mobile 端建立一个足够小但可复用的会话底座，使后续 auth feature 不需要把 token、snapshot、清理语义和启动恢复逻辑散落在页面或 service 中。

本 step 只解决三个问题：

- 本地会话快照放在哪里，由谁读写
- 应用启动时如何把本地快照推导为最小认证状态
- 路由层和请求层如何消费同一个状态 owner

## 非目标

本 step 不承担以下内容：

- 手机号登录提交
- refresh token 网络调用
- 协议确认状态扩展
- 设备会话管理
- 完整 analytics 埋点实现

## 架构

### 模块结构

```
lib/core/auth/
├── auth.dart                    # 统一导出
├── auth_state.dart              # 认证状态所有者
├── session_snapshot.dart        # 会话快照模型
└── session_storage.dart         # 存储抽象
```

### 边界划分

- `SessionSnapshot`：受控的本地会话快照模型，包含版本、token、userId 等最小字段
- `SessionStorage`：存储抽象，负责受控读写本地 session snapshot，处理 key 命名、版本和清理语义
- `AuthStateOwner`：认证状态所有者，负责把读取结果映射为最小认证状态，向路由层和请求层暴露统一读取入口
- `AppRouter`：消费 auth state owner 的结果，实现路由守卫
- `ApiClient`：只消费统一会话读取结果，不直接碰原始 secure storage

## Session Snapshot 结构

### 字段定义

```dart
class SessionSnapshot {
  final int version;           // 快照结构版本
  final String accessToken;    // 访问令牌
  final String refreshToken;   // 刷新令牌
  final String userId;         // 用户 ID
  final DateTime? expiresAt;   // 令牌过期时间（可选）
}
```

### 版本管理

- 当前版本：`1`
- 版本号用于后续迁移，确保向后兼容

### 验证规则

- `version` 必须存在且 >= 1
- `accessToken` 不能为空
- `refreshToken` 不能为空
- `userId` 不能为空
- `expiresAt` 可选，如存在需为有效 ISO8601 格式

## 认证状态

### 状态定义

使用 sealed class 确保状态处理完整性：

```dart
sealed class AuthState {
  bool get isBootstrapping;
  bool get isSignedOut;
  bool get hasAvailableSession;
  SessionSnapshot? get snapshot;
}

class AuthStateBootstrapping extends AuthState { ... }
class AuthStateSignedOut extends AuthState { ... }
class AuthStateSignedIn extends AuthState { ... }
```

### 状态流转

```
┌─────────────────┐
│  Bootstrapping  │  应用启动
└────────┬────────┘
         │
         ▼
┌────────────────┐
│ SessionStorage │  读取本地快照
│    .read()     │
└────────┬───────┘
         │
    ┌────┴────┬─────────────┐
    │         │             │
 Success    Empty       Corrupted
    │         │             │
    ▼         ▼             ▼
┌───────┐ ┌─────────┐  ┌──────────┐
│Signed │ │ Signed  │  │ 清理后   │
│  In   │ │   Out   │  │SignedOut │
└───────┘ └─────────┘  └──────────┘
```

## 启动恢复流程

### Bootstrap 集成

1. `AppBootstrap.run()` 初始化环境配置
2. `_initializeAuthState()` 创建 `SessionStorage` 和 `AuthStateOwner`
3. `AuthStateOwner.initialize()` 读取本地快照并推导状态
4. 状态推导完成后，`authStateOwner` 可被 `App` 和 `AppRouter` 消费

### 路由集成

```dart
// App 接收 authStateOwner
class App extends StatelessWidget {
  final AuthStateOwner authStateOwner;
  ...
}

// AppRouter 使用 authStateOwner 实现路由守卫
static GoRouter createRouter({
  required AuthStateOwner authStateOwner,
}) {
  return GoRouter(
    refreshListenable: authStateOwner,
    redirect: (context, state) {
      final authState = authStateOwner.state;
      // 受保护路由需要登录
      if (isProtectedRoute && !authState.hasAvailableSession) {
        return AppRoutes.login;
      }
      // 已登录用户访问登录页重定向到首页
      if (isAuthRoute && authState.hasAvailableSession) {
        return AppRoutes.home;
      }
      return null;
    },
    ...
  );
}
```

## 失败场景

### 本地快照损坏

处理流程：
1. `SessionStorage.read()` 返回 `SessionReadCorrupted`
2. `AuthStateOwner._handleCorruptedSnapshot()` 调用 `SessionStorage.clear()`
3. 状态设为 `AuthStateSignedOut`
4. 路由层自动重定向到登录页

### 存储读取失败

处理流程：
1. `SessionStorage.read()` 捕获异常
2. 返回 `SessionReadEmpty` 而非 `SessionReadCorrupted`
3. 避免触发不必要的清理操作
4. 状态设为 `AuthStateSignedOut`

## 清理入口

### 统一清理

`AuthStateOwner` 提供两个清理方法：

```dart
// 清理本地存储并更新状态
Future<bool> clearSession();

// 仅更新内存状态（用于 token 被服务端撤销）
void forceSignOut();
```

### 使用场景

- 用户主动登出：调用 `clearSession()`
- Token 刷新失败：调用 `forceSignOut()` 后由登录流程处理
- 快照损坏：自动清理并进入登出状态

## 与后续 steps 的关系

- `step-01` 建立应用壳入口边界
- `step-02` 提供 request pipeline，但还没有统一本地会话 owner
- 本 step 建立 owner 后，后续 auth feature 才有稳定宿主
- 后续登录、refresh、协议 gating 和设备会话都应扩展这个底座，而不是绕开它重新直连本地存储
