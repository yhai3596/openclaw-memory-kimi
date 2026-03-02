#!/bin/bash
# 企业微信客服群监控系统 - 运行脚本
# MVP版本

WORKSPACE="/root/.openclaw/workspace/projects/wecom-customer-service"
cd "$WORKSPACE"

echo "=== 企业微信客服群监控系统 ==="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

# 安装依赖
echo "[1/3] 检查依赖..."
pip3 install -q pyyaml requests 2>/dev/null || true

# 初始化数据库
echo "[2/3] 初始化数据库..."
python3 -c "
import sys
sys.path.insert(0, './scripts')
from service_monitor import Database
db = Database('./data/customer_service.db')
print('✅ 数据库初始化完成')
"

# 运行测试
echo "[3/3] 运行测试..."
echo ""
python3 scripts/service_monitor.py

echo ""
echo "✅ 测试完成"
echo ""
echo "数据文件: $WORKSPACE/data/customer_service.db"
echo "日志文件: $WORKSPACE/logs/"
echo "配置文件: $WORKSPACE/config/config.yaml"
