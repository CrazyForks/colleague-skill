# HEARTBEAT.md
# Uncomment tasks below to enable periodic execution.
# Default heartbeat interval: 30 minutes.

## share-daily-life
# Automatically share a daily life image for the active colleague.
# Requires: NANOBANANA_API_KEY set, Telegram channel configured.
#
# To enable: uncomment the block below and set COLLEAGUE_SLUG + CHAT_ID.
#
# ---task---
# name: share-daily-life
# schedule: daily at 20:00        # or: every 6h, every 30m, etc.
# run: |
#   python tools/share_life.py \
#     --slug "$COLLEAGUE_SLUG" \
#     --chat-id "$TELEGRAM_CHAT_ID"
# ---end---
