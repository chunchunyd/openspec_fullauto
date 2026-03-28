# 设计说明：Analytics Part1 Step 07 Duplicate Conflict 受控失败语义收口

## 目标

- 让 duplicate event 在 analytics 写入链路中被稳定识别为“受控重复”，而不再混入真实存储故障。

## 边界

- 只处理 duplicate conflict 分类、错误码与日志语义。
- 不在这一步引入新的重试队列、幂等表或异步补偿任务。
- 不改变服务端 emitter 的非阻塞原则。

## 方案

### 1. 保留预检查，但补齐数据库唯一约束兜底

- 现有 `existsByEventId` 预检查可以继续保留，用于普通 duplicate fast-path。
- 但数据库唯一约束冲突必须作为最终兜底，被识别成 duplicate 语义，而不是直接掉进 `StorageWriteError`。

### 2. `safe emitter` 区分 duplicate 与 storage failure

- `emitServerEventSafe` 对 duplicate conflict 返回明确的 duplicate error code。
- 真正的存储故障仍返回 `STORAGE_WRITE_FAILED`，避免两者混淆。

### 3. 日志分层

- duplicate conflict 只记受控 warning / info 语义。
- 真实写库异常才进入 storage failure error 语义。

## 风险与取舍

- 如果把 duplicate 直接当成功吞掉，虽然可以减少噪音，但会弱化“调用方是否发生异常重放”的可观察性。
- 因此本 change 优先选择“受控 duplicate 结果”，而不是伪装成成功。

## 验证重点

- 预检查命中 duplicate 时的返回语义。
- 数据库唯一约束冲突时的返回语义。
- duplicate 与真实 storage failure 在日志和错误码上可区分。
