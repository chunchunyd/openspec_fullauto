# Delta for Mobile Auth

## ADDED Requirements

### Requirement: mobile 客户端必须在已登录但未满足协议确认时保持 consent gate

mobile 客户端在已登录但未满足必要协议确认时，必须保持 consent gate，而不是仅凭存在 session 就直接放行完整产品空间。 The mobile client MUST keep users behind a consent gate until required agreements are confirmed.

#### Scenario: 启动恢复后仍缺必要确认

- WHEN 应用恢复到一个存在可用 session 的用户，并从服务端得到“仍缺必要协议确认”的 gating 结果
- THEN mobile 客户端必须继续停留在 consent gate
- AND 不得因为本地已有 session 就默认放行进入完整产品空间

### Requirement: mobile 客户端必须通过受控流程完成必要协议确认后再放行完整产品

mobile 客户端必须通过受控流程完成必要协议确认，并在服务端确认放行后才进入完整产品空间。 The mobile client MUST complete required consents through a controlled flow before granting full-product access.

#### Scenario: 完成全部必要协议确认

- WHEN 用户在 consent gate 中完成所有必要协议确认，且服务端返回放行结果
- THEN mobile 客户端必须将用户导入完整产品可达空间
- AND 后续启动恢复必须能够依据服务端当前 gating 真相继续保持该放行结果

#### Scenario: 协议确认部分失败

- WHEN 协议确认请求出现部分失败、网络失败或服务端仍未放行
- THEN mobile 客户端必须保持用户停留在 consent gate 并提供受控重试入口
- AND 不得把部分成功误判为完整放行
