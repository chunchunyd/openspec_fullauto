# 任务拆解：Mobile Foundation Step 04 反馈与错误边界原语

## 1. 实施前门禁

- [x] 同步最新 `dev/mobile-foundation`
- [x] 从 `dev/mobile-foundation` 切出 `feat/mobile-foundation-step-04-feedback-and-error-boundary-primitives`
- [x] 确认 `mobile-foundation-step-01-app-shell-entry-boundary` 与 `mobile-foundation-step-02-http-contract-and-request-pipeline` 已完成或达到可复用状态
- [x] 确认当前 step 只建立 feedback primitives 与错误边界，不混入具体 auth 页面和完整 telemetry 事件方案

## 2. 反馈原语

- [x] 建立统一的 loading / empty / error / retry feedback primitives 或等价页面壳
- [x] 让后续 auth 与其他 feature 可以复用这些最小反馈语义
- [x] 避免每个 feature 长期各自维护漂移的状态组件

## 3. 错误边界

- [x] 完成应用级未处理异常兜底路径，覆盖 Flutter 框架层、zone 或等价运行时入口
- [x] 建立从 request pipeline / runtime exception 到用户可理解反馈的统一映射入口
- [x] 确保未知异常不会直接向最终用户暴露原始堆栈或不透明黑屏

## 4. 文档与注释

- [x] 更新 `apps/mobile/README.md` 或等价模块说明，解释 feedback primitives 与错误边界的职责
- [x] 对错误映射或 fallback 中不直观的容错逻辑补必要注释

## 5. 验证与测试

- [x] 为 loading / empty / error / retry 的基础渲染补 widget 测试或等价验证
- [x] 为未处理异常进入受控 fallback 的行为补测试或等价验证
- [x] 如果本 step 新增或实质修改自动化测试文件，测试文件头注释必须写明完整执行命令

### 手动验收步骤

1. request 失败时，应进入受控错误反馈，而不是直接泄露底层原始错误
2. 页面空态和可重试态应能复用统一反馈组件，而不是各 feature 自己拼装
3. 运行时未处理异常触发后，应进入受控 fallback，而不是直接黑屏或暴露堆栈

## 6. 合并与收口

- [x] 当前 step 通过验收后，将 `feat/mobile-foundation-step-04-feedback-and-error-boundary-primitives` squash merge 回 `mobile-foundation-dev`
- [x] 不在本 change 内执行 `mobile-foundation-dev -> dev`，该操作由人工负责
