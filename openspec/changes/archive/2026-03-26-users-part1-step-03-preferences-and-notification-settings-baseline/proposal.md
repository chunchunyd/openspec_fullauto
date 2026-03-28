# 变更提案：Users Part1 Step 03 偏好与通知设置基线

## 为什么要做

`users-part1` 如果只停留在资料读取和资料编辑，后续用户侧的偏好开关、通知设置与最小个性化控制仍然没有正式宿主。本 step 作为 `part1` 的收口，只建立最小设置主数据与自我配置边界，不提前承诺推送投递、推荐策略执行或复杂隐私矩阵。

本批 change 继续沿用 `users-part1` 作为 series prefix，且 `part1` 到此仍只覆盖 self profile 与最小设置宿主。当前 step 复用前两步的资料宿主与 `packages/api_contracts` 导出链路，不新增新的 `libs/` 共享层前置 change。

## 本次变更包含什么

- 为偏好与通知设置建立最小持久化锚点与默认值语义
- 提供用户自我读取与更新设置的受控入口
- 限定首期必要开关的字段范围与局部更新语义

## 本次变更不包含什么

- Push 投递链路、站外通知渠道或模板系统
- 推荐排序策略执行与实验平台
- 复杂隐私圈层、黑名单或受众矩阵配置

## 预期结果

1. `users` 模块拥有首期可持续扩展的设置宿主。
2. 用户可以读取并修改自己的最小偏好与通知开关。
3. 后续通知、推荐或隐私能力可以在既有设置边界上增量扩展。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/users/*`
- `packages/api_contracts/openapi/openapi.json`
