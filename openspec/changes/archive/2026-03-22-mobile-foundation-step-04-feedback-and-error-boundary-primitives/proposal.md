# 变更提案：Mobile Foundation Step 04 反馈与错误边界原语

## 为什么要做

在 app shell、request pipeline 和 session storage 建立之后，mobile 端仍然缺少一套统一的用户可见反馈和应用级错误兜底。

如果没有这一步：

- 各 feature 会各自实现 loading、empty、error、retry，长期漂移
- 底层 request 错误和运行时异常会直接泄露到页面或调试输出
- 后续 auth 页面很难形成统一、可复用的失败语义

因此需要在正式铺开 auth 页面之前，先把反馈原语和错误边界原语独立收敛出来。

## 本次变更包含什么

本次变更聚焦移动端反馈与错误边界原语，范围包括：

- 建立统一的 loading / empty / error / retry feedback primitives
- 建立应用级未处理异常兜底与统一错误映射入口
- 让 request pipeline 与路由壳可以把失败结果映射为用户可理解的反馈

## 本次变更不包含什么

本次变更不包含以下内容：

- 具体 auth 页面文案细化
- 完整 analytics 事件上报
- 运营级埋点字典
- 风险策略 UI

## 预期结果

完成后，项目应具备以下结果：

1. 后续 auth 与其他 feature 可以复用统一的 loading / empty / error / retry 语义
2. request 失败与运行时异常有受控的页面反馈路径
3. 未处理异常不再直接向最终用户暴露原始堆栈或黑屏

## 影响范围

本次变更主要影响：

- `apps/mobile/lib/core/error`
- `apps/mobile/lib/app`
- `apps/mobile/README.md`
