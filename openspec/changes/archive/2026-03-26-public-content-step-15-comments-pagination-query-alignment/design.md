# 设计说明：Public Content Step 15 评论分页查询契约对齐

## 目标

本 step 的目标是让 comments list 的分页输入在真实 HTTP 请求下按文档稳定工作，而不是继续依赖测试里直接传 number 的理想路径。

## 当前缺口

当前 `ListCommentsQueryDto.limit` 虽然声明为 `number` 并使用 `@IsInt()` 约束，但 HTTP 查询字符串天然以 string 进入 controller。

在仅开启 `transform: true`、未开启 `enableImplicitConversion` 的前提下，如果 DTO 本身不显式声明转换，`limit=20` 仍会在验证阶段被视为 string，从而把合法请求误判为 400。

## 方案选择

### 1. 优先采用局部显式转换

本 step 优先给 comments list 的 `limit` 参数补充 `@Type(() => Number)` 或等价显式转换，而不是在全局打开隐式转换。

这样做的原因是：

- 改动边界更小
- 不会把其他 controller 的 query / body 转换语义一起改变
- 更符合当前仓库在 content / feed 分页 DTO 上已经采用的显式做法

### 2. 用 controller 级回归测试覆盖真实输入形态

测试应覆盖字符串查询参数，而不是只在 service 层传 number。至少需要覆盖：

- `limit=20` 通过
- `limit=0` 被拒绝
- `limit=101` 被拒绝

## 非目标

本 step 不处理：

- comments list 父帖子 404 语义
- OpenAPI 导出文件是否已经同步
- 评论以外的其他互动分页输入
