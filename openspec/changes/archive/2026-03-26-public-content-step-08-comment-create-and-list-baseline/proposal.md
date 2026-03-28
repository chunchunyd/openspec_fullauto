# 变更提案：Public Content Step 08 评论创建与列表基线

## 为什么要做

公开帖子只有点赞与收藏还不够，评论是首期内容互动链路里的另一条核心主线。当前仓库还没有评论数据模型和 API 边界，因此需要把评论创建与列表读取单独拆成一个小 step。

## 本次变更包含什么

- 建立公开帖子评论的最小数据模型与 API 边界
- 支持发表评论与按帖子读取评论列表
- 返回评论作者最小摘要与作者类型

## 本次变更不包含什么

- 多级楼中楼评论
- 评论点赞
- 评论审核结论与运营后台处理

## 预期结果

1. 公开帖子有正式的评论写入与读取主线。
2. 评论对象能够和帖子、作者类型建立稳定关联。
3. 举报与互动摘要后续可以围绕同一条评论主线继续演进。

## 影响范围

- `prisma/schema.prisma`
- `apps/api/src/modules/interactions/*`
- `apps/api/src/modules/content/*`
- `packages/api_contracts/openapi/openapi.json`

