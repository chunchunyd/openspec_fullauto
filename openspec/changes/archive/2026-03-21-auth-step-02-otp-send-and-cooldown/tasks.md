# 任务拆解：Auth Step 02 验证码发送与冷却控制

## 1. 实施前门禁

- [x] 从最新 `dev` 切出 `feat/auth-step-02-otp-send-and-cooldown` 并确认主项目工作树边界
- [x] 确认 `auth-step-01-data-model-baseline` 已完成或其数据落位已可复用
- [x] 阅读 `libs/sms/README.md`、`libs/cache/README.md` 与当前 `auth` spec

## 2. 契约与发送链路

- [x] 为 `auth` capability 建立本次 step 的 spec delta
- [x] 定义手机号归一化规则与发送验证码接口 contract
- [x] 如接口对外暴露，执行 `openapi-export` 并确认共享契约产物更新

## 3. auth 发码实现

- [x] 在 `apps/api/src/modules/auth` 中实现验证码生成逻辑
- [x] 建立 auth 模块自己的验证码 / 冷却 / 发送频控缓存语义
- [x] 复用 `libs/sms` 发送登录验证码

## 4. 冷却与频控

- [x] 实现单手机号冷却时间控制
- [x] 实现单手机号或单请求来源的基础发送频控
- [x] 明确频控命中和短信发送失败时的返回语义

## 5. 验证与测试

- [x] 为手机号归一化、验证码生成和缓存语义补单元测试
- [x] 为冷却时间与发送频控补等价验证
- [x] 验证短信 provider 失败时不会留下难以解释的缓存状态

### 手动验收步骤

1. 请求发送验证码一次，应成功返回冷却时间等必要元数据
2. 冷却期内再次请求，应被受控拒绝或返回受控结果
3. 连续多次请求后，应触发发送频控
4. 本地 fake / debug provider 下，应能稳定看到发送链路结果
