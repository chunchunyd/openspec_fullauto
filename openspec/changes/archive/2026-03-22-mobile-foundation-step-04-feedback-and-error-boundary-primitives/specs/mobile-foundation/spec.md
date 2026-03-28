# Delta for Mobile Foundation

## ADDED Requirements

### Requirement: mobile 客户端必须提供统一的基础页面反馈原语

mobile 客户端必须提供统一的基础页面反馈原语，以避免各 feature 长期维护彼此漂移的 loading、empty、error 和 retry 语义。 The mobile client MUST provide shared page-feedback primitives for loading, empty, error, and retry states.

#### Scenario: 页面进入加载态

- WHEN 任意 mobile 页面进入受支持的加载态
- THEN 客户端必须能够复用统一的加载反馈组件
- AND 不得要求每个 feature 各自重新定义最小加载语义

#### Scenario: 页面进入空态或失败态

- WHEN 任意 mobile 页面进入空态、失败态或可重试状态
- THEN 客户端必须能够复用统一的反馈组件或等价页面壳
- AND 错误与重试入口不得长期分散在页面层各自实现

### Requirement: mobile 客户端必须对未处理异常提供应用级受控兜底

mobile 客户端必须对未处理异常提供应用级受控兜底，以避免最终用户直接面对原始堆栈、黑屏或不透明崩溃。 The mobile client MUST provide app-level controlled fallback behavior for unhandled exceptions.

#### Scenario: 运行时出现未处理异常

- WHEN Flutter 框架层、zone 或等价运行时路径出现未处理异常
- THEN mobile 客户端必须进入受控的异常兜底路径
- AND 不得直接把原始堆栈信息暴露给最终用户

#### Scenario: 页面需要把错误转为用户可理解结果

- WHEN 页面或公共组件需要把底层异常映射为用户可理解的反馈
- THEN mobile 客户端必须能够经过统一错误映射层处理
- AND 页面不应长期直接依赖底层异常类型进行分支判断
