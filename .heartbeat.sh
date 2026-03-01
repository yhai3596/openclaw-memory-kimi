#!/bin/bash
# 心跳记忆检查脚本
# 由 OpenClaw 心跳自动执行

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
LOG_FILE="$WORKSPACE/.heartbeat.log"
DATE=$(date '+%Y-%m-%d')
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATETIME] ====== 心跳检查开始 ======" >> "$LOG_FILE"

# 1. 执行备份
echo "[$DATETIME] 执行自动备份..." >> "$LOG_FILE"
cd "$WORKSPACE" && ./.backup.sh >> "$LOG_FILE" 2>&1

# 2. 检查关键记忆文件
for file in IDENTITY.md USER.md SOUL.md; do
    if [ ! -f "$WORKSPACE/$file" ]; then
        echo "[$DATETIME] 警告: 缺失关键文件 $file" >> "$LOG_FILE"
    fi
done

# 3. 检查今日记忆文件
TODAY_FILE="$MEMORY_DIR/${DATE}.md"
if [ ! -f "$TODAY_FILE" ]; then
    echo "[$DATETIME] 创建今日记忆文件: ${DATE}.md" >> "$LOG_FILE"
    mkdir -p "$MEMORY_DIR"
    echo "# ${DATE} 记忆日志" > "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"
    echo "## 心跳记录" >> "$TODAY_FILE"
    echo "- ${DATETIME}: 系统心跳，记忆系统正常运行" >> "$TODAY_FILE"
else
    # 追加心跳记录
    echo "- ${DATETIME}: 系统心跳" >> "$TODAY_FILE"
fi

# 4. 检查远程仓库
if ! git -C "$WORKSPACE" remote get-url origin >/dev/null 2>&1; then
    echo "[$DATETIME] 提醒: 未配置远程仓库，请运行 git remote add origin <url>" >> "$LOG_FILE"
fi

echo "[$DATETIME] ====== 心跳检查完成 ======" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
