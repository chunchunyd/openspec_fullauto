# 设计说明：Public Content Step 14 持久化 migration 收口

## 目标

本 step 的目标不是重新设计 public-content 的数据模型，而是把已经进入当前 schema 的结构正式回补到 migration 历史中，让仓库重新满足“schema 与 migration 一致”的交付基线。

## 边界

本 step 只处理以下问题：

- schema 已存在但 migration 未提交的 comments / follows / likes / favorites / reports 相关结构
- 与这些结构直接相关的 enum、index、foreign key 和唯一约束
- 与 migration 回补直接相关的最小说明更新

本 step 不处理：

- 新的互动对象或新的举报对象类型
- 任何 HTTP contract、OpenAPI 或前端消费字段变化
- 已有 public-content 业务逻辑的继续扩张

## 迁移策略

### 1. 以当前 schema 为目标状态

当前 `prisma/schema.prisma` 已经表达了 public-content 相关持久化真相源，因此回补 migration 时应以“让 migration 历史追上当前 schema”为目标，而不是回退 schema 重新压缩已归档 step 的能力。

### 2. 采用补齐式 migration，而不是重写旧历史

当前推荐做法是：

- 保留既有 migration 历史不动
- 在当前 series 头部补一条或少量有边界的 migration
- 让这批 migration 覆盖 public-content 已落地但尚未进入历史的结构

这样可以避免改写已归档 change 对应的旧历史，也更符合当前 series 的收口语义。

### 3. 用 drift 校验确认真正收口

补 migration 后，应至少做两类验证：

- `prisma migrate diff` 或等价 drift 校验为空
- `pnpm db-generate` 或等价 client 生成链路仍然可用

如果 drift 仍然存在，不应把 migration 回补视为完成。

## 风险与取舍

### 风险：把“缺失的旧结构”误和“新的 schema 扩张”混在一起

为避免新的 schema 漂移被偷偷夹带，本 step 应先明确 review 已确认的缺口范围，只补已经进入当前 public-content 主线的结构。

### 风险：只补 migration，不验证对齐结果

如果只生成 migration 文件而不做 drift 校验，仍可能留下 enum / index / foreign key 级别的隐性差异。因此验收必须包含对齐校验，而不是只看文件是否存在。
