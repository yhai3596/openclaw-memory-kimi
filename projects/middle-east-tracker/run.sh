#!/bin/bash
# 中东局势追踪 - 主控脚本

WORKSPACE="/root/.openclaw/workspace/projects/middle-east-tracker"
INTERVAL=${1:-600}  # 默认10分钟

echo "=== 中东局势追踪系统 ==="
echo "更新间隔: ${INTERVAL}秒"
echo ""

cd "$WORKSPACE"

# 1. 抓取新闻
echo "[1/3] 抓取新闻..."
python3 scripts/fetcher.py

# 2. 生成网页
echo "[2/3] 生成网页..."
python3 scripts/generator.py

# 3. 提交到 Git
echo "[3/3] 备份数据..."
cd /root/.openclaw/workspace
git add -A
git commit -m "Update: 中东局势追踪 $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true

echo ""
echo "✅ 完成"
echo "网页位置: $WORKSPACE/web/index.html"
