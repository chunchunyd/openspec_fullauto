# 变更提案：Public Content Step 13 公开互动边界加固

## 为什么要做

`series/public-content` 本轮验收还暴露出另一组集中在 `interactions` 模块的问题：

- likes / favorites 目前只按帖子状态判断是否可互动，没有把“作者仍然公开”纳入边界
- comments list 没有校验父帖子是否仍然公开可读，不存在帖子也会返回 `200 + []`
- step-11 引入 `BehaviorSignalService` 后，follows / comments / reports 的 service 测试 provider 没有同步补齐，导致 interaction 回归护栏失效

这个 step 继续沿用 `public-content` 作为 series prefix，只收口公开互动对象边界与对应回归护栏，不扩展新的互动能力主题。

## 本次变更包含什么

- 收紧 likes / favorites 的公开互动判断，只允许对当前仍可公开互动的帖子建立新互动关系
- 收紧 comments list 的父帖子公开可读校验，并让不存在或不再公开的父帖子稳定返回 404
- 对齐 comments list `limit` 查询参数的数字转换与分页校验
- 恢复 follows / comments / reports 的 service 回归测试，并补齐代表性行为信号断言

## 本次变更不包含什么

- public feed / public detail 的可选鉴权读侧增强
- `updatedAt` 或 feed/content 读侧 DTO 的契约回对齐
- 新的举报对象类型、关注产品语义或复杂评论能力

## 预期结果

1. 非公开帖子不会继续被普通消费侧新建点赞或收藏，也不会通过 comments list 继续暴露可见评论结果。
2. comments list 的 404 契约、分页输入与真实接口行为重新一致。
3. interactions 模块针对边界与行为信号的回归测试重新恢复可用，后续修复不再失去护栏。

## 影响范围

- `apps/api/src/modules/interactions/*`
- `packages/api_contracts/openapi/openapi.json`
