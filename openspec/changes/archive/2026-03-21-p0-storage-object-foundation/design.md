# 设计说明：P0 对象存储共享层基建

## 目标

本次设计的目标不是一次性做完全部媒体系统，而是先建立一个最小但稳定的对象存储共享层，让后续 `content`、`feed` 和 Agent 资料能力能直接复用。

重点解决四件事：

1. `libs/storage` 到底负责什么
2. 业务模块如何通过共享抽象存取对象
3. 本地开发与测试如何不依赖真实云存储
4. 文件标识、访问 URL 和元信息边界如何统一

## 分层模型

### 1. 共享存储运行时层：`libs/storage`

职责：

- 定义对象存储 port
- 统一上传请求、对象标识和结果模型
- provider adapter 接线
- provider 选择与配置读取
- fake / local provider
- 最小访问 URL 或等价访问结果抽象

不负责：

- 业务模块自己的媒体语义
- 图片裁剪、转码、水印和异步处理流水线
- 业务层的审核策略

### 2. 业务模块层

职责：

- 决定“为什么要存这个文件”
- 决定该文件属于头像、帖子图片、帖子封面还是其他业务媒体
- 决定如何把对象标识与业务实体关联

这意味着：

- `content` 负责“帖子图片 / 封面怎么组织”
- `libs/storage` 负责“文件如何上传、存储和返回访问结果”

## 首期能力范围

首期建议只做对后续业务最需要复用的部分：

- `StoragePort`
- 统一上传命令
- 统一对象标识结果
- 统一公开访问 URL 或等价读取结果
- fake / local provider

本次刻意不纳入：

- 批量媒体处理
- 图片处理流水线
- 签名直传
- CDN 与复杂缓存策略
- 多供应商自动切换

## 为什么先做对象存储抽象

当前已知会直接受益的能力包括：

- `content` 的帖子图片与封面
- `feed` 的图片 / 封面消费
- 未来 `agents` 的头像、封面与资料素材

如果没有共享抽象，后续极容易出现：

- 某个业务模块先临时接云厂商 SDK
- 另一个业务模块再接一套不同命名和结果边界
- 本地开发时无法稳定模拟存储结果

因此这次设计遵循：

- 先统一对象存储抽象
- 业务语义后续按 capability 自己接入

## 请求与结果模型

建议首期至少统一以下几个概念：

- 上传请求
  - `bucket` 或等价逻辑容器
  - `key` 或由共享层生成对象 key
  - `contentType`
  - `body`
  - `metadata`
- 上传结果
  - `objectKey`
  - `provider`
  - `contentType`
  - `size`
  - `publicUrl` 或等价访问结果

如果首期不想让业务模块直接参与原始 `bucket/key` 管理，也可以让共享层统一生成 object key，但业务模块至少需要拿到稳定的对象标识，便于和数据库实体关联。

## URL 与对象标识边界

首期最容易漂移的地方是“数据库里到底存什么”。

建议原则如下：

- 业务实体优先存稳定对象标识，例如 `objectKey`
- 公开访问 URL 作为共享层生成或派生结果返回
- 不建议业务表把某个云厂商的完整 URL 当作长期唯一真相源

这样后续：

- 切 CDN
- 切域名
- 调整公开 / 私有访问策略

都更容易演进。

## fake / local provider

本地开发和测试必须有稳定替身。

建议首期提供：

- fake provider
  - 不真正上传云对象
  - 返回可预测的对象标识与访问结果
- local provider
  - 可选
  - 将文件落到本地开发目录并返回本地可访问路径或模拟 URL

要求：

- 本地开发不应默认要求真实云存储账号
- fake / local provider 的使用方式应在 README 中明确说明
- 测试不应默认依赖外部云服务成功

## 命名与目录前缀

虽然具体业务目录前缀可以后续扩展，但首期建议从第一天统一一个基础规则。

例如：

- `content/posts/`
- `content/covers/`
- `agents/avatars/`

要求：

- 业务前缀表达资源语义
- 对象 key 不应裸露敏感信息
- 文件名冲突规避策略应统一，而不是每个业务模块各自发明

## 与 observability 的关系

`libs/storage` 后续应复用共享日志能力：

- 上传开始 / 成功 / 失败
- provider 名称
- `correlationId`
- 对象标识

但日志中不应直接输出敏感文件内容或不必要的原始二进制信息。

## 与 queue 的关系

未来如果图片处理、转码、审核或搬运需要异步化，推荐关系如下：

- 业务模块先通过 `libs/storage` 完成基础对象落库或对象标识生成
- queue 决定是否异步触发后续媒体处理任务
- `worker` 消费 job
- 具体文件访问仍复用 `libs/storage`

也就是说：

- `queue` 不替代 `libs/storage`
- `libs/storage` 也不负责 job 管理

## 首期目录建议

```txt
libs/storage/
├─ README.md
└─ src/
   ├─ index.ts
   ├─ storage.module.ts
   ├─ storage.port.ts
   ├─ storage.types.ts
   ├─ storage.tokens.ts
   └─ providers/
      ├─ fake-storage.provider.ts
      └─ ...
```

如果当前暂时不准备完整拆开文件，也至少应保证：

- port
- types
- provider

这三类职责不要继续停留在空文件里。

## 与后续 change 的关系

该 change 完成后，后续最直接受益的是：

- `content` 的帖子图片与封面接入
- `feed` 的媒体结果消费
- 未来 `agents` 的头像 / 封面能力

后续 change 不再重新争论“对象存储 provider 放哪、数据库里存 object key 还是完整 URL、本地怎么调试”。
