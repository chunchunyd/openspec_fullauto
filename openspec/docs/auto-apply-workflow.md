# Auto Apply 当前流程

本文档记录当前项目里 `openspec/auto/auto_apply.sh` 的协作方式，用来说明系列化 change 在自动执行时的真实流程边界。

这是一份项目自定义工作流说明，不替代 OpenSpec 官方文档。

## 1. 适用场景

- 适用于 `xxx-step-01-*`、`xxx-step-02-*` 这类同系列 change。
- 适用于需要依赖图、并行执行、断点续传和系列级 git 管理的自动流程。
- 适用于当前仓库这种“主仓库根目录通过符号链接暴露 `./openspec/`，其真实仓库在仓库外单独维护”的结构。

## 2. 总体原则

当前流程采用“并行开发，串行回合并”的模型：

- 父脚本负责调度，不直接替子进程完成实现工作。
- OpenSpec 本身承载长期项目规则；父脚本传给子进程的主 prompt 只补充当前 worktree 运行上下文和少量自动化环境约束，避免噪音稀释 `tasks.md` 同步这一基础机制。
- 每个 change 在独立 worktree 中执行，避免多个进程共用一个工作目录。
- worktree 从基准 ref 以 detached `HEAD` 方式创建，而不是直接检出同一个集成分支。
- 对系列 change，父脚本负责标准化 Git 编排：准备 `series/<series-prefix>` 集成分支、切出实现分支、接收子进程交回的 `ready_for_merge` 结果、按队列检查实现分支已干净交棒，并串行执行 `--no-ff merge`。
- 子进程 agent 在自己的 worktree 内专注于实现、测试、文档和 `tasks.md` 的非自动化任务同步。
- 系列 change 在子进程内只做到“可交棒的实现完成态”；真正的 handoff cleanup、`feat/<change-id> -> series/<series-prefix>` merge、archive 和后续 cleanup 由父脚本维护显式队列后串行托管。
- 对系列 change，切出实现分支是硬门禁：在任何会写文件的动作发生前，必须先离开 detached `HEAD` 或 `series/<series-prefix>`，进入 `feat/<change-id>`、`fix/<change-id>` 或 `chore/<change-id>`。

## 3. 目录与脚本

- 主调度脚本：[auto_apply.sh](/home/ccyd/workspace/nenggan/openspec/auto/auto_apply.sh)
- 依赖图格式说明：[dependency-graph-format.md](/home/ccyd/workspace/nenggan/openspec/auto/dependency-graph-format.md)
- 系列规则说明：[change-series-management-rules.md](/home/ccyd/workspace/nenggan/openspec/docs/change-series-management-rules.md)

## 4. 父脚本职责

`auto_apply.sh` 的默认职责是：

- 在主仓库根目录调用 OpenSpec CLI
- 读取依赖图并按依赖调度 change
- 为每个 change 创建独立 git worktree
- 校验 worktree 已自动继承主仓库跟踪的 `openspec/` 符号链接
- 从 `.env.example` 生成 `.env`
- 为每个 change 分配独立本地监听端口，避免并行测试抢端口
- 对系列 change 自动准备 `series/<series-prefix>` 与实现分支，并勾选对应的自动化分支门禁 checkbox
- 恢复会话存档目录中的已完成 change，支持断点续传
- 在真正启动任何 change 之前，先对目标 change 运行一轮 OpenSpec 结构预检；如果缺少 delta、Scenario 或其他基础 artifact 结构错误，脚本会直接 fail fast，不会先消耗一次实现执行
- 以 `tasks.md` 作为 change 进度真相源；如果 active change 目录不存在，会继续到 `changes/archive/` 中查找同名已归档 change 的 `tasks.md`
- 当某个 change 的一次 apply 结束后仍有 checkbox 未完成时，先启动一个额外的 tasks-sync 子进程，只负责把 `tasks.md` 对齐到真实完成状态
- 如果 tasks-sync 后仍然 incomplete，再启动评估子进程判断是否真的需要人工介入
- 如果评估认为不需要人工介入，则带着更明确的聚焦提示再自动重试一次 apply；如果评估认为需要，则停止整轮脚本并展示建议
- 当 Claude 子进程返回 `API Error: 429` / `code=1302` 这类速率限制结果时，父脚本会按退避节奏自动等待并重试当前这次 Claude 调用，而不是立刻把 change 判成失败
- 如确实需要，父脚本可以通过 `--allow-local-db-reset` 或环境变量 `OPENSPEC_AUTO_ALLOW_LOCAL_DB_RESET=1` 显式授权子进程在“当前 worktree 关联的本地开发/测试数据库”阻塞实现或验证时，直接执行删库重建、reset、reseed 或从头迁移；这条授权只适用于可丢弃的本地数据库，不适用于任何共享、远端、staging 或 production 数据库
- 对系列 change，子进程在验证通过后不会自己做最终 Git 收口，而是写出 `ready_for_merge` 结果交给父脚本；父脚本会按“完成时间”把这些 change 放入显式 merge 队列，再串行检查实现分支是否已干净交棒、必要时启动 Claude handoff cleanup、执行 `--no-ff merge`、必要时启动 Claude merge fallback、勾选自动化收口 checkbox，并在成功后继续 archive / cleanup
- 在 change 执行后决定是否 validate、archive、cleanup worktree
- 对系列 change，在成功 archive 后，父脚本会先尝试删除已经完成生命周期的本地实现分支；若分支仍被占用、未真正合入系列集成分支或删除失败，会在摘要中明确提示
- cleanup 时先直接尝试 `git worktree remove`，只有直接清理失败或 worktree 仍处于脏状态时，才启动 Claude fallback 检查并重试清理
- 接收到 `Ctrl+C` / `SIGINT` / `SIGTERM` 时，级联终止当前所有子进程树，再输出摘要退出

`auto_apply.sh` 默认不负责：

- 不执行 `series/<series-prefix> -> dev`

## 5. worktree 创建方式

每个 change 的 worktree 都应从基准 ref 以 detached `HEAD` 方式创建。

这样做的原因是：

- Git 不允许两个 worktree 同时检出同一个分支
- 如果直接把多个 worktree 都建在 `series/<series-prefix>` 上，会互相冲突
- detached worktree 只是以该分支当前提交为起点，不会占住这个分支

当前基准 ref 选择规则是：

- 优先 `series/<series-prefix>`
- 如果不存在，再退回 `dev`
- 再不行时才退回其他可用 ref

当前仓库的 `openspec/` 由主项目仓库跟踪为符号链接，因此：

- 新 worktree 会天然继承这个 `openspec/` 入口
- 父脚本只负责检查该入口存在
- 父脚本不应在 worktree 内重新创建、替换或覆盖 `openspec` 符号链接

## 6. 子进程 agent 职责

子进程 agent 在自己的 worktree 内负责：

- 按 OpenSpec apply instructions 实现 change
- 更新 `openspec/changes/<change-id>/tasks.md`，并保持只有可执行动作使用 checkbox；人工职责或说明性内容使用普通项目符号或备注
- 运行必要测试或验证
- 保证实现结果留在父脚本准备好的实现分支上；如果 worktree 里已经存在该 change 的未提交状态，应先把它当成继承现场处理，再继续实现；在成功交棒前，agent 自己应提交有效改动并把实现分支清理干净，让子进程能把 change 交给父脚本的 merge 队列

子进程 agent 不应：

- 直接修改主仓库工作目录
- 在主仓库路径执行分支切换
- 在 detached `HEAD` 或 `series/<series-prefix>` 上做实现性改动
- 在自动化流程里手动接管标准化的分支切出、最终 merge 回 `series/<series-prefix>` 或 `series/<series-prefix> -> dev`
- 自行 archive change

## 7. 父脚本托管的回合并方式

对系列 change，当前推荐由父脚本托管标准化回合并，而不是让子进程自己处理。

推荐步骤是：

- 父脚本先在 change worktree 上自动准备实现分支，并同步头部自动化 checkbox
- agent 完成实现、测试和其余任务后，子进程只会把自己标记为 `ready_for_merge`，交回父脚本
- 父脚本把所有 `ready_for_merge` 的系列 change 按完成时间放入显式队列
- 父脚本取出队首 change 后，若发现实现分支仍有未提交改动，会先启动一次专门的 handoff cleanup pass，要求 agent 整理继承现场、提交有效改动并把实现分支清理干净
- 随后父脚本直接在原 change worktree 中切到 `series/<series-prefix>`，并串行执行 `git merge --no-ff -m "<change-id>" <implementation-branch>`
- 如果直接 merge 或 merge commit 失败，父脚本会先启动一次 Claude merge fallback，在原 change worktree 中检查并尝试完成冲突解决与提交；只有 fallback 仍无法收口时，才转交人工
- merge commit 完成后，父脚本勾选结尾的自动化 merge checkbox，并把原 worktree detach 到新的集成提交，释放实现分支与系列分支占用
- 成功 archive 后，父脚本会尝试删除已完成生命周期的本地实现分支
- 最后再按配置决定是否清理 change worktree

## 8. 为什么需要 merge 锁

多个 step 可以并行开发，但不能同时把结果回合并到同一个 `series/<series-prefix>`。

原因有两层：

- Git 层面：同一分支不能被多个 worktree 同时检出
- 流程层面：前一个 step merge 完后，后一个 step 需要基于更新后的集成分支继续收口

因此当前规则是：

- 编码阶段可以并行
- `feat/* -> series/<series-prefix>` 回合并阶段必须串行，且由父脚本通过显式 merge 队列统一托管

在当前这种“同一个主仓库 + 多个 worktree”的模型下，父脚本统一在串行阶段切换原 change worktree 到集成分支并完成 merge，就已经足够承担这一层互斥，不再需要让子进程自己等待重试。

另外还有一条实践约束：

- 主工作区不应长期检出 `series/<series-prefix>` 这类系列集成分支
- 否则并行 step 在各自 worktree 中执行最终回合并时，会被 Git 直接拦住
- 主工作区平时应停在 `dev`、个人功能分支，或 detached `HEAD`
- 只有在人工检查系列集成结果或执行 `series/<series-prefix> -> dev` 时，才临时切到该系列集成分支
- 检查完成后应尽快切离该分支，释放给子 worktree 使用

## 9. 会话存档与断点续传

每一组 change 会对应一个固定命名的会话目录：

```text
openspec/auto/logs/.auto-apply-run.<session-key>/
```

常见情况下，`session-key` 就是系列前缀，例如：

```text
openspec/auto/logs/.auto-apply-run.mobile-foundation/
```

它用于保存：

- 每个 change 的 `.result`
- 每个 change 的端口配置文件
- 会话恢复所需的执行状态

脚本启动时会优先从这里恢复已经成功归档的 change，把它们视为已完成依赖。

如果某个 change 已经从 active 列表消失，但在 `changes/archive/` 中还能找到对应的 `tasks.md`：

- 脚本会把 archive 中的 `tasks.md` 作为该 change 的真实完成状态来源
- 若 archive 中 `tasks.md` 已全部完成，则恢复为已完成依赖
- 若 archive 中 `tasks.md` 反而仍未完成，则标记为需要人工处理，而不是误报“目录缺失”

依赖图文件默认放在：

```text
openspec/auto/deps/deps.<series-prefix>.json
```

如果显式传入多个 `--deps`，脚本会先合并这些依赖图后再调度。

## 10. 多 `--prefix` / 多 `--deps` 规则

`auto_apply.sh` 支持重复传入多个 `--prefix` 和多个 `--deps`，但边界很明确：

- 多个 `--prefix` 只用于彼此独立的系列并跑
- 多个 `--deps` 只用于合并彼此独立的依赖图

如果合并后的依赖图里出现跨 `series prefix` 的依赖，例如 `B-step-02` 依赖 `A-step-03`，脚本会在执行前直接 fail fast，并提示：

- 当前这几组 change 不适合继续作为多个系列并跑
- 应回到 change 规划阶段，把这些相互依赖的 workstream 合并成一个以目标能力命名的 `series prefix`

另外，和数据库相关的可选授权建议这样使用：

- 默认不传 `--allow-local-db-reset`
- 只有在明确知道当前 worktree 会操作的是本地、一次性、可重建的开发或测试数据库时，才打开这个开关
- 打开后，agent 仍应优先使用项目现有的标准 reset / rebuild 命令，并在交棒说明里写清自己执行了什么命令、为什么需要这样做

## 11. 推荐执行顺序

对于一个标准系列 change，推荐流程如下：

1. 先生成该系列全部 change。
2. 生成 `openspec/auto/deps/deps.<series-prefix>.json`。
3. 运行 `auto_apply.sh`，让父脚本按依赖启动多个 detached worktree。
4. 子进程 agent 在各自 worktree 中沿着父脚本准备好的实现分支开发、测试、更新 `tasks.md`。
5. 如果某个 change 一次 apply 结束后仍有 checkbox 未完成，父脚本会先发起一次 tasks-sync，只做 `tasks.md` 对账。
6. 如果 tasks-sync 后仍然 incomplete，父脚本再发起一次“是否需要人工介入”的评估。
7. 评估结论为“不需要人工介入”时，父脚本会带着聚焦提示再重跑一次 apply；若结论为“需要人工介入”，父脚本会停止并展示建议。
8. 子进程在任务完成且校验通过后，把 change 标记为 `ready_for_merge`；父脚本随后按队列顺序，在原 change worktree 中串行把实现分支用 `--no-ff merge` 合回 `series/<series-prefix>`，再把 worktree detach 到新的集成提交。
9. 父脚本完成 archive，并尝试删除已完成生命周期的本地实现分支。
10. `series/<series-prefix> -> dev` 由人工完成。

## 12. 示例

以 `mobile-foundation` 为例：

1. `auto_apply.sh` 从 `series/mobile-foundation` 或 `dev` 创建多个 detached worktree。
2. `mobile-foundation-step-02-*` 的 worktree 会被父脚本自动切到 `feat/mobile-foundation-step-02-*`。
3. `mobile-foundation-step-03-*` 的 worktree 会被父脚本自动切到 `feat/mobile-foundation-step-03-*`。
4. 两者可以并行编码和测试。
5. 当 `step-02` 达到可验收状态后，父脚本在它原来的 change worktree 中切到 `series/mobile-foundation`。
6. 父脚本在该原 worktree 中执行 `--no-ff merge` 并提交，然后把该 worktree detach 到新的集成提交。
7. `step-03` 若随后也需要回合并，同样由父脚本在串行阶段处理。

多前缀并行示例：

```bash
./openspec/auto/auto_apply.sh --all \
  --prefix users-part1- \
  --prefix analytics-part1-
```

前提是这两个 series 彼此独立，依赖图中不存在交叉引用；如果存在交叉依赖，应重新规划为一个目标导向的 series prefix。

## 13. 当前默认结论

当前项目推荐的默认方式是：

- 用 `auto_apply.sh` 负责调度和隔离
- 用子进程 agent 负责 step 内签出、实现、测试
- 用 Git 自身的 worktree 分支占用约束负责系列级串行回合并
- 用人工负责 `series/<series-prefix> -> dev`
