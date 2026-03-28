# 变更提案：Public Content Step 14 持久化 migration 收口

## 为什么要做

`series/public-content` 在 step-07 到 step-13 期间已经把 comments、follows、likes、favorites、reports 等持久化结构写进了当前 `prisma/schema.prisma`，但最新验收表明这些结构还没有对应的正式 migration 历史。

如果继续保持“schema 已存在、migration 未提交”的状态，新环境或 CI 在依赖真实数据库结构时会直接缺表，这会让 public-content 系列虽然通过了局部单测，却无法作为可交付能力稳定落地。

本 step 继续沿用 `public-content` 作为 series prefix，只收口 Prisma schema 与 migration 历史的一致性，不扩展新的互动模型或内容能力。

## 本次变更包含什么

- 为 public-content 已落地的 comments、follows、likes、favorites、reports 等持久化结构补齐正式 Prisma migration
- 校验当前 `prisma/schema.prisma` 与已提交 migration 历史不再漂移
- 保证新环境可以通过 migration 获得与当前 public-content 代码一致的数据库结构

## 本次变更不包含什么

- 新的 Prisma 模型、字段或索引扩张
- public-content 的读写行为返工
- 共享 OpenAPI 契约导出

## 预期结果

1. `prisma/schema.prisma` 与已提交 migration 历史重新对齐。
2. 新环境不需要依赖“直接拿当前 schema 建库”这种隐式前提，就能跑起 public-content 相关能力。
3. 后续继续推进 public-content 收口时，不会再被 migration 缺口反复卡住。

## 影响范围

- `prisma/schema.prisma`
- `prisma/migrations/*`
- 必要时的 `prisma/README.md` 或等价说明
