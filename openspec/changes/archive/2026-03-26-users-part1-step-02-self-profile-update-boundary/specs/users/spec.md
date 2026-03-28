# Delta for Users

## ADDED Requirements

### Requirement: 系统必须允许已登录用户受控更新自己的资料

系统必须允许已登录用户受控更新自己的资料，并只接受明确白名单中的可编辑字段。 The system MUST allow authenticated users to update their own profiles through a controlled boundary.

#### Scenario: 更新可编辑资料字段

- WHEN 已登录用户提交受支持的资料字段更新
- THEN 系统必须保存该更新或其等价结果
- AND 后续自我读取必须返回更新后的受控资料

#### Scenario: 尝试修改非资料归属字段

- WHEN 用户尝试通过 users 写入 auth-owned 身份字段或未开放字段
- THEN 系统必须拒绝该写入
- AND 不得让资料更新入口越权修改认证主状态
