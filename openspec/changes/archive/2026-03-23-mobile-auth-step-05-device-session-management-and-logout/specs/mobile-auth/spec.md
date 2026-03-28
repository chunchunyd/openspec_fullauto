# Delta for Mobile Auth

## ADDED Requirements

### Requirement: mobile 客户端必须允许用户查看并管理设备会话

mobile 客户端必须允许已登录用户查看并管理设备会话，包括识别当前设备与移除其他设备会话。 The mobile client MUST allow signed-in users to view and manage device sessions.

#### Scenario: 查看设备会话列表

- WHEN 已登录用户进入设备会话管理入口
- THEN mobile 客户端必须展示设备会话列表、当前设备标记和基础设备信息
- AND 不得把原始后端响应直接暴露为未加工数据结构

#### Scenario: 移除其他设备会话

- WHEN 用户请求移除一个非当前设备的会话
- THEN mobile 客户端必须通过受控流程调用会话移除接口并更新页面结果
- AND 不得把“移除其他设备”与“退出当前设备”混成同一个动作

### Requirement: mobile 客户端必须支持当前设备退出登录并清理本地会话

mobile 客户端必须支持当前设备退出登录，并在退出后清理本地会话与受保护访问能力。 The mobile client MUST support logging out the current device and clearing the local session.

#### Scenario: 当前设备退出登录

- WHEN 已登录用户在当前设备执行退出登录
- THEN mobile 客户端必须清理本地会话并退出受保护空间
- AND 后续不得继续把该设备视为已登录状态
