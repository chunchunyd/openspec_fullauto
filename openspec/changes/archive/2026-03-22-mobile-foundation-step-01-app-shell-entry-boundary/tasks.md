# 任务拆解：Mobile Foundation Step 01 应用壳入口边界

## 1. 实施前门禁

- [x] 如果 `dev/mobile-foundation` 不存在，则从最新 `dev` 切出 `dev/mobile-foundation`
- [x] 从 `dev/mobile-foundation` 切出 `feat/mobile-foundation-step-01-app-shell-entry-boundary`
- [x] 确认旧 `auth-mobile-*` 与旧 `mobile-foundation` spec 仅作为历史残余，不作为当前实施输入
- [x] 确认当前 step 只建立 app shell 入口边界，不混入 request pipeline、session storage、feedback primitives 和 telemetry hooks

## 2. 启动入口与环境分层

- [x] 将 `main.dart` 与 `main_*.dart` 从 Flutter 模板入口收敛为项目自己的启动入口
- [x] 建立 `app_bootstrap` 的最小初始化主线，明确启动顺序与失败返回
- [x] 为开发、测试、预发、生产环境建立清晰的配置落点和非法配置失败语义

## 3. 应用壳与路由边界

- [x] 建立 `app.dart` 与 `app_router.dart` 的最小可运行实现
- [x] 建立 public / auth / protected 的顶层路由空间与统一 fallback
- [x] 让应用启动后进入项目自己的壳，而不是 Flutter 默认 counter demo

## 4. 文档与规格收口约定

- [x] 更新 `apps/mobile/README.md`，说明最小启动方式、环境入口与 app shell 边界

## 5. 验证与测试

- [x] 为环境选择与 bootstrap 失败语义补单元测试或等价验证
- [x] 为 public / auth / protected 初始分流与未知路由 fallback 补 widget 测试或等价验证
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. 启动 `apps/mobile` 后，应进入项目自己的 app shell，而不是 Flutter 默认示例页
2. 使用不同 `main_*.dart` 入口启动时，应能进入受控的环境配置路径
3. 访问未知路由时，应进入统一 fallback，而不是散落到页面层各自兜底

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-foundation-step-01-app-shell-entry-boundary` squash merge 回 `dev/mobile-foundation`
- [x] 不在本 change 内执行 `dev/mobile-foundation -> dev`，该操作由人工负责
