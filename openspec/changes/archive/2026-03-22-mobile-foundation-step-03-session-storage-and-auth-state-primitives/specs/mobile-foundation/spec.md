# Delta for Mobile Foundation

## ADDED Requirements

### Requirement: mobile 客户端必须通过受控存储抽象管理本地会话快照

mobile 客户端必须通过受控存储抽象管理本地会话快照，以避免页面层直接操作原始 secure storage、key 命名和清理语义。 The mobile client MUST manage local session snapshots through a controlled storage abstraction instead of exposing raw storage details to pages.

#### Scenario: 读写本地会话快照

- WHEN mobile 客户端需要读取、写入或清理本地会话快照
- THEN 这些操作必须通过统一的受控存储抽象完成
- AND 页面层不应长期直接操作原始本地存储 key

#### Scenario: 本地快照损坏

- WHEN 本地会话快照缺字段、格式损坏或明显非法
- THEN mobile 客户端必须以受控方式清理该快照
- AND 不得因为损坏快照直接导致页面层崩溃

### Requirement: mobile 客户端必须根据本地会话快照推导最小认证状态

mobile 客户端必须根据本地会话快照推导最小认证状态，以支撑后续 auth、协议 gating 和受保护路由分流。 The mobile client MUST derive minimal authentication state from the local session snapshot for downstream routing and request decisions.

#### Scenario: 启动时恢复本地状态

- WHEN mobile 应用启动并尝试恢复本地会话状态
- THEN 客户端必须能够把快照推导为受控的最小认证状态
- AND 该结果必须能够被路由层和请求层消费

#### Scenario: 本地不存在可用快照

- WHEN 本地不存在任何可用会话快照
- THEN mobile 客户端必须把当前状态视为未登录或等价 visitor 状态
- AND 不得误把用户直接导入受保护路由空间
