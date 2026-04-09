---
name: share-daily-life
description: 生成并分享同事的日常生活图片，支持 /share-life 命令和 heartbeat 定时触发
user-invocable: true
triggers:
  - /share-life
---

# share-daily-life skill

你负责帮同事"晒日常"——根据当前同事的 persona，生成一张符合他/她气质的日常生活图片，发送到 Telegram。

---

## 触发方式

### 方式一：用户主动触发

用户发送 `/share-life` 时执行：

```
Step 1 → 确认当前同事
Step 2 → 生成图片 prompt（基于 persona 动态生成）
Step 3 → 异步生图，立即回复"生成中"
Step 4 → 图片完成后自动发到 Telegram
```

### 方式二：Heartbeat 定时触发

heartbeat 触发时，如果 HEARTBEAT.md 中有 `share-daily-life` 任务，自动执行一次分享。

---

## Step 1：确认当前同事

检查当前会话中是否已激活某个同事的 slug：
- 已激活：直接使用，告知用户"正在为 {name} 生成日常图片..."
- 未激活：询问用户选择哪位同事，或列出 `colleagues/` 目录下可用的同事

---

## Step 2：生成图片（异步）

执行以下命令，**立即返回**，不等待图片生成完成：

```bash
python tools/share_life.py \
  --slug "{colleague_slug}" \
  --chat-id "{telegram_chat_id}"
```

收到 `job_id` 后，立即回复用户：

```
📸 正在为 {name} 生成日常图片，稍后发送到这里～
job_id: {job_id}
```

---

## Step 3：（可选）检查进度

用户发送 `/share-life status {job_id}` 时：

```bash
python tools/image_generator.py check --job-id "{job_id}"
```

根据状态回复：
- `pending` / `running`：还在生成中，请稍等
- `done`：已发送 ✅
- `error`：生成失败，告知用户错误原因

---

## Step 4：自定义场景

用户可以指定场景，例如 `/share-life 下班路上` 或 `/share-life 打游戏`：

```bash
python tools/share_life.py \
  --slug "{colleague_slug}" \
  --chat-id "{telegram_chat_id}" \
  --scene "{用户指定的场景}"
```

---

## Dry Run（调试用）

不实际生图，只输出会生成的 prompt：

```bash
python tools/share_life.py \
  --slug "{colleague_slug}" \
  --chat-id "0" \
  --dry-run
```

---

## 注意事项

- 图片生成是**异步的**，模型不应等待生成完成再回复
- Telegram 图片发送走 Bot API 直接调用（绕过 openclaw 的已知 bug）
- NANOBANANA_API_KEY 需在环境变量中设置，或在 `image_generator.py` 中配置
