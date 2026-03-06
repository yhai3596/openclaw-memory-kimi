#!/bin/bash
# 自动备份脚本 - 推送到 GitHub
# 每30分钟执行一次

cd /root/.openclaw/workspace

# 检查是否有变更
if git diff --quiet && git diff --staged --quiet; then
    echo "$(date): 无变更，跳过备份" >> .backup.log
    exit 0
fi

# 添加所有变更
git add -A

# 提交
git commit -m "自动备份: $(date '+%Y-%m-%d %H:%M:%S')"

# 推送到 GitHub
if git push origin master; then
    echo "$(date): 备份成功" >> .backup.log
else
    echo "$(date): 备份失败" >> .backup.log
fi
