#!/bin/bash
# 自动记忆备份脚本
# 由 OpenClaw 自动执行

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/.backup.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 开始自动备份..." >> "$LOG_FILE"

cd "$WORKSPACE" || exit 1

# 检查是否有变更
if git diff --quiet HEAD 2>/dev/null && git diff --staged --quiet 2>/dev/null; then
    echo "[$DATE] 没有变更，跳过备份" >> "$LOG_FILE"
    exit 0
fi

# 添加所有变更
git add -A

# 提交变更，使用当前日期作为提交信息
COMMIT_MSG="Auto-backup: $DATE

变更内容:
$(git status --short)

备份类型: 自动定时备份"

git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

# 如果有远程仓库，推送
if git remote get-url origin >/dev/null 2>&1; then
    git push origin master >> "$LOG_FILE" 2>&1
    echo "[$DATE] 已推送到远程仓库" >> "$LOG_FILE"
else
    echo "[$DATE] 警告: 未配置远程仓库" >> "$LOG_FILE"
fi

echo "[$DATE] 备份完成" >> "$LOG_FILE"
