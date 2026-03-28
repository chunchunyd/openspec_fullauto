# Auto Apply 依赖图格式说明

本文档说明 [auto_apply.sh](/home/ccyd/workspace/nenggan/openspec/auto/auto_apply.sh) 支持的依赖 JSON 格式，以及脚本如何根据依赖关系自动并行调度 change。

## 作用

依赖图文件用于告诉脚本：

- 哪些 change 可以立即开始
- 哪些 change 必须等待上游完成后才能开始
- 哪些 change 可以在依赖满足后并行执行

脚本读取依赖图后，会自动寻找“所有依赖都已经成功完成”的节点，并按 `--max-parallel` 的限制启动新进程执行。

并行执行时，脚本会为每个 change 创建独立的 git worktree，避免多个 Claude 进程在同一个主仓库目录里互相切换分支。

这能解决“并发 change 共用同一个工作目录”带来的分支踩踏问题，但不能替代合理的依赖拆分。如果两个 change 会长期修改同一批核心文件，即使 worktree 隔离了分支，也仍然可能在后续合并时产生高冲突，因此依赖图里仍应把真实会互相阻塞的 change 串行化。

如果你额外传入 `--cleanup-worktrees`，脚本会在某个 change 成功归档后尝试删除它对应的 worktree：

- 先直接执行 `git worktree remove`
- 如果该 worktree 仍有未提交改动，或直接删除失败，再启动一次 Claude fallback 检查并重试清理
- 如果 fallback 之后仍未删除成功，才会在摘要里记为 `cleanup-failed`

创建新 worktree 时，脚本还会在该 worktree 根目录下：

- 从 `.env.example` 生成 `.env`
- 为当前 change 分配一组独立的本地监听端口
- 更新 `.env` 中的 `API_PORT`、`WORKER_PORT`、`AGENT_RUNTIME_MOCK_PORT`、`AGENT_RUNTIME_GRPC_PORT` 以及对应的 `AGENT_RUNTIME_BASE_URL`、`AGENT_RUNTIME_GRPC_TARGET`

这样并行跑多个 change 时，本地起 API / worker / runtime mock 做测试，不会默认抢同一组监听端口。共享基础设施端口，例如 PostgreSQL 和 Redis，默认保持不变。

当前仓库的 `openspec/` 由主项目仓库跟踪为一个指向外部规格仓库的符号链接，因此新 worktree 会自动继承它。父脚本只负责检查该入口存在，不会在 worktree 内重新创建或覆盖 `openspec` 符号链接。

对 `xxx-step-xx-*` 这类系列 change，脚本默认会托管标准化的 Git 编排：

- 从 `series/<series-prefix>` 或 `dev` 这类基准 ref 创建隔离 worktree
- 自动准备标准化的实现分支，并同步 `tasks.md` 头部的自动化 checkbox
- 把中间实现、测试和非自动化任务同步交给 Claude 按 `tasks.md` 在该 worktree 内执行
- 在验证通过后，子进程只把 change 交成 `ready_for_merge`；父脚本再按完成时间进入显式 merge 队列，串行切换原 change worktree 到 `series/<series-prefix>`，把实现分支用 `--no-ff merge` 合回去，再把 worktree detach 到新的集成提交

在当前这种“同一个主仓库 + 多个 worktree”的模型下，系列级 merge 互斥由父脚本维护的串行 merge 队列承担，不需要再依赖子进程自己等待重试。

脚本还会为每一组 change 维护一个持久化会话目录，命名为：

```text
openspec/auto/logs/.auto-apply-run.<session-key>/
```

其中 `session-key` 会优先使用系列前缀，例如 `mobile-foundation`。脚本启动时会先从这个目录恢复已经成功归档的 change，把它们视为已完成依赖，从而支持断点续传。

如果某个依赖 change 已经不在 active `changes/` 里，但在 `changes/archive/` 中还能找到对应的 `tasks.md`，脚本会继续使用 archive 中的 `tasks.md` 作为真相源来恢复它的状态，而不是误判成“缺失 change”。

旧版随机目录名例如 `.auto-apply-run.2ojxIQ`，如果其中包含当前这组 change 的结果文件，脚本会自动迁移成新的固定目录名。

## 支持的 JSON 格式

支持两种等价格式。

### 1. 对象映射格式

键是 change id，值是它依赖的上游 change 列表。

```json
{
  "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline": [],
  "mobile-foundation-step-02-ui-feedback-and-error-primitives": [
    "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline"
  ],
  "mobile-foundation-step-03-network-contract-and-request-pipeline": [
    "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline"
  ],
  "mobile-foundation-step-04-session-storage-and-auth-state-primitives": [
    "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline",
    "mobile-foundation-step-03-network-contract-and-request-pipeline"
  ]
}
```

### 2. 显式数组格式

适合后续想在每个节点旁边继续扩字段时使用。

```json
{
  "changes": [
    {
      "name": "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline",
      "dependsOn": []
    },
    {
      "name": "mobile-foundation-step-02-ui-feedback-and-error-primitives",
      "dependsOn": [
        "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline"
      ]
    },
    {
      "name": "mobile-foundation-step-03-network-contract-and-request-pipeline",
      "dependsOn": [
        "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline"
      ]
    },
    {
      "name": "mobile-foundation-step-04-session-storage-and-auth-state-primitives",
      "dependsOn": [
        "mobile-foundation-step-01-bootstrap-shell-and-routing-baseline",
        "mobile-foundation-step-03-network-contract-and-request-pipeline"
      ]
    }
  ]
}
```

## 字段语义

- `name`: 当前 change 的 id，也就是 `openspec/changes/<change-id>/` 的目录名。
- `dependsOn`: 当前 change 依赖的上游 change id 列表。

如果你用对象映射格式，那么：

- key 等价于 `name`
- value 等价于 `dependsOn`

## 调度规则

脚本的调度语义是：

1. 没有依赖的节点可以立即启动。
2. 某个节点只有在 `dependsOn` 中的所有 change 都成功完成后才会启动。
3. 如果多个节点同时满足依赖，它们可以并行启动。
4. 并发数受 `--max-parallel <n>` 控制。
5. 如果某个上游 change 失败，所有依赖它的下游 change 会被标记为 `blocked`。
6. 如果某个上游 change 执行后任务仍未全部完成，或仍停留在 `ready_for_merge` 队列里尚未被父脚本真正收口为 `success`，下游都不会被解锁。

这里的“成功完成”指的是脚本内部把该 change 判定为：

- Claude 执行成功
- 如果没有 `--skip-validate`，则 `openspec validate` 通过
- `tasks.md` 中任务全部完成
- 如果启用了自动归档，归档也成功

## 多文件与多前缀

如果你这样调用：

```bash
./openspec/auto/auto_apply.sh --deps ./openspec/auto/deps/deps.mobile-foundation.json
```

脚本会把依赖图里的全部节点都纳入调度。

如果你这样调用：

```bash
./openspec/auto/auto_apply.sh \
  --deps ./openspec/auto/deps/deps.users-part1.json \
  --deps ./openspec/auto/deps/deps.analytics-part1.json
```

脚本会先合并这些依赖图，再对合并后的节点集合做调度。

如果你这样调用：

```bash
./openspec/auto/auto_apply.sh --all --prefix users-part1- --prefix analytics-part1-
```

脚本会筛出匹配这些前缀的 active changes；如果没有显式传入 `--deps`，它还会优先尝试自动推断：

- `openspec/auto/deps/deps.users-part1.json`
- `openspec/auto/deps/deps.analytics-part1.json`

## 根节点与传递依赖

如果你这样调用：

```bash
./openspec/auto/auto_apply.sh mobile-foundation-step-04-session-storage-and-auth-state-primitives --deps ./openspec/auto/deps/deps.mobile-foundation.json
```

脚本会自动把这个目标节点以及它的全部传递依赖一起纳入执行范围。也就是说，不需要手动把 `step-01`、`step-03` 再额外写一次。

## 并行示例

例如有这组依赖：

```json
{
  "step01": [],
  "step02": ["step01"],
  "step03": ["step01"],
  "step04": ["step02", "step03"]
}
```

调度顺序会是：

1. `step01` 先执行
2. `step01` 成功后，`step02` 和 `step03` 可以并行执行
3. `step02` 和 `step03` 都成功后，`step04` 才能开始

## 失败与阻塞示例

例如：

```json
{
  "step01": [],
  "step05": [],
  "step08": ["step01", "step05"]
}
```

如果：

- `step01` 成功
- `step05` 失败

那么：

- `step08` 不会启动
- 脚本会把 `step08` 标记为 `blocked`

## 循环依赖

脚本会检查循环依赖。

例如下面这种写法是不允许的：

```json
{
  "step01": ["step02"],
  "step02": ["step01"]
}
```

如果存在环，脚本会在启动前直接报错，不会进入执行阶段。

## 跨系列依赖限制

如果合并后的依赖图里出现跨 `series prefix` 的依赖，例如：

```json
{
  "users-part1-step-03-profile-settings": [],
  "analytics-part1-step-02-user-profile-tracking": [
    "users-part1-step-03-profile-settings"
  ]
}
```

脚本会在执行前直接 fail fast，而不会尝试在运行时替你补 merge。

原因是：

- `users-part1-step-03-*` 和 `analytics-part1-step-02-*` 默认会落在不同的 `series/<series-prefix>` 集成线上
- 即使上游 change 在 OpenSpec 状态上已经完成，下游系列的代码基线也不一定已经包含它

正确做法是：

- 把这几组相互依赖的 change 回收到一个共同的、以目标能力命名的 `series prefix`
- 让它们在同一条 `series/<series-prefix>` 集成线上推进

## 建议写法

- 一个文件只描述一组相关 workstream 的依赖图。
- `dependsOn` 尽量只写真正阻塞执行的前置 change，不要把“只是逻辑上相关”的 change 也塞进去。
- 如果两个 change 只是共享同一 capability，但文件改动和执行路径互不阻塞，不要强行串行。
- 依赖图优先描述“什么时候可以开始”，而不是“最终希望什么顺序看起来更整齐”。
- 如果多个 workstream 会相互依赖，优先在 change 规划阶段直接使用一个以目标能力命名的 `series prefix`，不要事后靠多 `--prefix` 拼接。

## 推荐命名

建议把依赖图文件放在 `openspec/auto/deps/` 下，并使用能看出主题的名字，例如：

- `openspec/auto/deps/deps.mobile-foundation.json`
- `openspec/auto/deps/deps.auth-mobile.json`
- `openspec/auto/deps/deps.release-2026-03-22.json`

## 使用示例

跑完整个依赖图：

```bash
./openspec/auto/auto_apply.sh --deps ./openspec/auto/deps/deps.mobile-foundation.json
```

限制最多 2 个并发：

```bash
./openspec/auto/auto_apply.sh --deps ./openspec/auto/deps/deps.mobile-foundation.json --max-parallel 2
```

在成功归档后自动清理干净的 worktree：

```bash
./openspec/auto/auto_apply.sh \
  --deps ./openspec/auto/deps/deps.mobile-foundation.json \
  --max-parallel 2 \
  --cleanup-worktrees
```

只跑某个目标 change 及其传递依赖：

```bash
./openspec/auto/auto_apply.sh mobile-foundation-step-04-session-storage-and-auth-state-primitives \
  --deps ./openspec/auto/deps/deps.mobile-foundation.json \
  --max-parallel 2
```

只演练调度，不真正调用 Claude：

```bash
./openspec/auto/auto_apply.sh --deps ./openspec/auto/deps/deps.mobile-foundation.json --dry-run
```
