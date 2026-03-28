# Change 系列管理规则

本文档记录本项目独立于 OpenSpec 官方文档的系列化 change 管理规则，重点约束 `xxx-step-xx-*` 这类按步骤推进的 change。

自动执行时的完整流程说明，另见 [auto-apply-workflow.md](/home/ccyd/workspace/nenggan/openspec/docs/auto-apply-workflow.md)。

## 1. 适用范围

- 当多个 change 属于同一功能主题，并且 change id 采用 `xxx-step-01-*`、`xxx-step-02-*` 这类连续命名时，视为一个 change 系列。
- `step-xx` 之前的前缀视为该系列的 `series prefix`。
- 例如：`mobile-foundation-step-03-network-contract-and-request-pipeline` 的 `series prefix` 是 `mobile-foundation`。
- 如果多个 workstream 实际围绕同一个目标能力相互依赖，应在创建阶段直接共用一个以目标命名的 `series prefix`，不要先拆成多个系列再交叉引用。

## 2. Git 分支规则

### 2.1 系列集成分支

- 每个系列都应有一个上级集成分支，命名为 `series/<series-prefix>`。
- `step-01` 开始实施前，应先从最新 `dev` 切出 `series/<series-prefix>`。
- 如果后续 step 接手时 `series/<series-prefix>` 已存在，应先同步该分支，而不是重新从 `dev` 新切。

### 2.2 每个 step 的实现分支

- 包括 `step-01` 在内的每个 step，都应从 `series/<series-prefix>` 再切出自己的实现分支。
- 实现分支命名仍沿用原规则：
  - `feat/<change-id>`
  - `fix/<change-id>`
  - `chore/<change-id>`
- 一个 step 的实现分支只承载当前这个 change，不混做同系列的其他 step。
- 对系列 change，“切出实现分支”是实施硬门禁：在任何实现性编辑、代码生成、格式化、构建或可能写文件的测试动作发生前，都必须先进入该 step 自己的实现分支。
- 不允许在 detached `HEAD` 或 `series/<series-prefix>` 上直接开展实现工作；这些状态只允许用于起点定位、临时同步或最终回合并。

### 2.3 step 完成后的回合并

- 每个 step 完成并通过验收后，应先将其实现分支合并回 `series/<series-prefix>`。
- 默认优先使用 `--no-ff merge`，保留实现分支上的阶段性提交历史，并让一个 step 在上级集成分支上对应一个清晰结果提交。
- `series/<series-prefix>` 合并回 `dev` 由人工把关执行，不属于 agent 或自动化脚本的默认职责。
- `dev -> main` 的发布合并继续由人工执行。
- 如果使用 `openspec/auto/auto_apply.sh` 跑系列化 change，脚本会托管标准化的 Git 编排：准备 `series/<series-prefix>`、切出实现分支、让子进程只做到 `ready_for_merge`、再由父脚本按完成时间进入显式队列，串行检查实现分支是否已干净交棒、执行 `--no-ff merge`，并同步对应的自动化 checkbox。
- 子进程 agent 不再负责标准化的“切出实现分支”和“回合并到 `series/<series-prefix>`”动作；但它仍负责实现、验证、阶段性提交，以及在交棒前把实现分支清理干净。
- 对通过自动化成功完成并归档的系列 step，本地 `feat/<change-id>`、`fix/<change-id>` 或 `chore/<change-id>` 实现分支会进入生命周期收口阶段；脚本会在确认其已真正合入 `series/<series-prefix>` 且不再被任何 worktree 占用后自动删除该本地分支。
- 主工作区不应长期停留在 `series/<series-prefix>` 这类系列集成分支上；否则会阻塞并行 step 在各自 worktree 内完成最终回合并。主工作区平时应使用 `dev`、个人功能分支，或 detached `HEAD`，仅在人工检查系列集成结果或执行 `series/<series-prefix> -> dev` 时临时切入该系列分支。

## 3. tasks.md 的固定写法

- 只有“agent 在本 change 内应该执行、完成后可以明确打勾”的动作才使用 checkbox。
- 人工职责、范围排除、长期约束和“本 change 不执行某操作”这类说明，必须使用普通项目符号、编号列表或备注段落，不要写成 checkbox。

### 3.1 头部必须出现的分支门禁

对 `xxx-step-xx-*` 系列，`tasks.md` 头部必须写出固定的自动化分支规则，供父脚本稳定识别。

固定写法如下：

```md
## 1. 实施前门禁

- [ ] 自动化确认系列集成分支 `series/mobile-foundation` 已就绪（若不存在则从最新 `dev` 创建）
- [ ] 自动化从 `series/mobile-foundation` 切出 `feat/mobile-foundation-step-01-bootstrap-entrypoint` 实现分支，并将当前 worktree 绑定到该分支
- [ ] 在进入 `feat/mobile-foundation-step-01-bootstrap-entrypoint` 之前，不进行任何实现性编辑、生成器、格式化、构建或测试写文件动作
- [ ] 确认当前 step 只实现本 change 的范围，不混入同系列其他 step
```

要求：

- 前两条必须保持“自动化确认系列集成分支 ... 已就绪”与“自动化从 ... 切出 ... 实现分支，并将当前 worktree 绑定到该分支”这两个句式，不要自由改写。
- `<implementation-branch>` 必须填成真实分支名，例如 `feat/<change-id>`、`fix/<change-id>` 或 `chore/<change-id>`。
- 这两条 checkbox 保留给 `openspec/auto/auto_apply.sh` 自动执行与自动勾选；agent 不应在自动化流程里手动接管。

### 3.2 结尾必须出现的 merge 规则

对 `xxx-step-xx-*` 系列，`tasks.md` 结尾必须写出固定的自动化收口规则。

固定写法如下：

```md
## X. 合并与收口

- [ ] 自动化将 `feat/mobile-foundation-step-01-bootstrap-entrypoint` merge 回 `series/mobile-foundation`，保留实现分支上的阶段性提交历史
- 说明：`series/mobile-foundation -> dev` 不在本 change 内执行，该操作由人工负责
```

要求：

- 第一条必须保持“自动化将 ... merge 回 ...，保留实现分支上的阶段性提交历史”这个句式，不要改写成其他口吻。
- merge checkbox 保留给父脚本在验证通过后串行执行并自动勾选；agent 不应在自动化流程里手动完成这一步。
- `series/<series-prefix> -> dev` 继续保留为普通说明，不写成 checkbox。

### 3.3 提交类任务的写法

如果 `tasks.md` 中出现提交类任务，例如阶段性提交、继承现场整理提交或交接前收口提交，该任务必须显式引用 [git-commit-guidelines.md](/home/ccyd/workspace/nenggan/openspec/docs/git-commit-guidelines.md)。

推荐写法：

```md
- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定提交本阶段改动，并确保提交标题与正文完整说明本次结果和原因
- [ ] 按 `openspec/docs/git-commit-guidelines.md` 中的约定整理继承现场并提交，确认无效残留已安全清理
```

要求：

- 不要只写“及时 commit”
- 不要只写“提交代码”
- 任务文本必须让接手者知道应参考哪份提交规范

## 4. 依赖图文件

- 当同一系列的全部 change 已经生成后，应在 `openspec/auto/deps/` 下创建依赖图 JSON。
- 文件命名约定为 `deps.<series-prefix>.json`。
- 依赖图只表达真实阻塞关系，不表达“看起来更整齐”的顺序偏好。
- 自动化脚本并行执行时，应为每个 change 使用独立 git worktree，而不是共用同一个主仓库目录。
- 自动化脚本应为每个系列维护固定命名的会话存档目录，例如 `openspec/auto/logs/.auto-apply-run.mobile-foundation/`，并在启动时从中恢复已成功归档的 step，作为断点续传依据。
- 如果需要同时传入多个 `--prefix` 或多个 `--deps`，这些系列必须彼此独立；一旦依赖图里出现跨 `series prefix` 的依赖，脚本会直接 fail fast。
- 如果自动化提示存在跨系列依赖，不要尝试靠运行时补 merge；应回到 change 规划阶段，把相互依赖的 workstream 合并成一个以目标能力命名的 `series prefix`。
- 依赖图格式与脚本用法详见 [dependency-graph-format.md](/home/ccyd/workspace/nenggan/openspec/auto/dependency-graph-format.md)。

示例：

```json
{
  "mobile-foundation-step-01-bootstrap-entrypoint": [],
  "mobile-foundation-step-02-app-env": [
    "mobile-foundation-step-01-bootstrap-entrypoint"
  ],
  "mobile-foundation-step-03-routing-shell": [
    "mobile-foundation-step-01-bootstrap-entrypoint"
  ]
}
```

## 5. change 粒度规则

在已经具备系列分支、step 回合并和依赖图之后，change 粒度应优先收束得更细。

推荐标准是：

- 一个 change 只交付一个主目标。
- 一个 change 最好只对应一个主要验收路径。
- 一个 change 最好只围绕一个主要边界落点，例如启动入口、环境配置、路由壳、网络层、会话恢复，而不是把多个主落点并在一起。
- 标题如果需要使用“X、Y 与 Z”才能说明范围，默认先判断是否还能拆分。
- 只有当多个内容共享同一实现入口、无法独立验证，或拆分后会导致频繁相互阻塞时，才保留在同一个 change。

## 6. 对 `mobile-foundation` 的建议

`mobile-foundation` 这一类客户端基础建设很容易天然写大，因此更适合按“主边界”来拆，而不是按“方便描述的大段主题”来拆。

例如，下面这种标题通常偏大：

- `bootstrap-shell-and-routing-baseline`

更适合的拆法通常是：

- `bootstrap-entrypoint`
- `app-env-layering`
- `routing-shell-boundary`

这种拆法的前提，是每个子 change 都有自己的：

- 独立实施分支
- 明确回合并路径
- 可表达的依赖图
- 独立验收标准

只要这四点具备，细拆通常比大步长 change 更稳、更容易并行，也更容易在中途调整范围。
