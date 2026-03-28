# 变更提案：Mobile Foundation Step 01 应用壳入口边界

## 为什么要做

`apps/mobile` 当前仍停留在 Flutter 默认 demo 入口，`main.dart` 直接渲染模板页，而 `main_dev.dart`、`main_staging.dart`、`main_test.dart`、`main_prod.dart` 以及 `app/bootstrap`、`app/routing` 等目录大多还是空骨架。

在这种状态下直接开始 mobile auth，会立刻遇到这些基础问题：

- 没有项目自己的启动主线，后续初始化顺序无处承载
- 环境分层没有真实落位，开发、测试、预发和生产无法受控区分
- 顶层路由空间和 app shell 不存在，后续 auth/public/protected 分流没有稳定宿主
- 旧 `auth-mobile` 与旧 `mobile-foundation` 文案已经弃用，当前需要一个新的可靠起点

因此需要先用一个足够小但可运行的 step，把 mobile 端真正的应用壳入口边界立起来。

## 本次变更包含什么

本次变更聚焦移动端应用壳入口边界，范围包括：

- 将 `main.dart` 与 `main_*.dart` 从模板入口收敛为项目自己的启动入口
- 建立 `app_bootstrap`、`app.dart` 与 `app_router.dart` 的最小可运行主线
- 建立 public / auth / protected 的顶层路由空间与统一 fallback
- 为开发、测试、预发、生产环境保留清晰的环境配置落点
- 为本系列后续 change 形成新的 capability 重建起点

## 本次变更不包含什么

本次变更不包含以下内容：

- API request pipeline
- OpenAPI contract 消费
- 本地会话存储
- auth state owner
- 页面级 loading / empty / error / retry primitives
- 埋点事件字典或具体 analytics SDK 接线

## 预期结果

完成后，项目应具备以下结果：

1. `apps/mobile` 不再以 Flutter 默认 demo 作为正式入口
2. mobile 端具备项目自己的 bootstrap 主线与环境落点
3. 顶层 public / auth / protected 路由空间与 fallback 已有明确边界
4. 后续 request、session、feedback 与 auth feature 可以围绕同一套 app shell 继续推进

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/main.dart`
- `apps/mobile/lib/main_*.dart`
- `apps/mobile/lib/app/bootstrap`
- `apps/mobile/lib/app/env`
- `apps/mobile/lib/app/routing`
- `apps/mobile/lib/app/shell`
- `apps/mobile/README.md`
- `openspec/specs/mobile-foundation` 在本系列归档时的重建基线
