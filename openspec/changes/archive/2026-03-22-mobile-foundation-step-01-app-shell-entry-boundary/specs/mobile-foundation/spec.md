# Delta for Mobile Foundation

## ADDED Requirements

### Requirement: mobile 客户端必须提供项目自己的应用壳入口边界

mobile 客户端必须提供项目自己的应用壳入口边界，以替代 Flutter 默认 demo 入口并为后续 feature 提供受控宿主。 The mobile client MUST provide a project-owned app-shell entry boundary instead of relying on the default Flutter demo entrypoint.

#### Scenario: 通过默认入口启动应用

- WHEN 开发者或运行环境通过 `main.dart` 启动 mobile 应用
- THEN 客户端必须进入项目自己的 bootstrap 与 app shell 主线
- AND 不得继续把 Flutter 默认 counter demo 当作正式应用入口

#### Scenario: 通过环境入口启动应用

- WHEN 开发者或运行环境通过 `main_dev.dart`、`main_test.dart`、`main_staging.dart` 或 `main_prod.dart` 启动应用
- THEN 客户端必须进入与该入口对应的受控环境配置路径
- AND 不得静默回退到与入口不匹配的默认环境

### Requirement: mobile 客户端必须提供 public、auth 与 protected 的顶层路由空间

mobile 客户端必须提供 public、auth 与 protected 的顶层路由空间，以承载后续认证分流和受保护页面边界。 The mobile client MUST provide top-level public, auth, and protected route spaces for subsequent authentication and protected-page flows.

#### Scenario: 应用完成 bootstrap 后进入首个路由空间

- WHEN mobile 应用完成最小 bootstrap 并准备展示首个界面
- THEN 客户端必须进入 public、auth 或 protected 三类顶层空间之一
- AND 后续 feature 不得自行重新发明顶层宿主入口

#### Scenario: 路由未命中

- WHEN 客户端收到未知路由、非法入口或未命中的页面路径
- THEN 客户端必须进入统一 fallback
- AND 不得把 fallback 逻辑分散给各业务页面各自处理
