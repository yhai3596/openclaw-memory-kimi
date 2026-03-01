#!/bin/bash
# ListenHub Skill 部署脚本
# 用于 OpenClaw 中枢节点

set -e

echo "=== ListenHub Skill 部署 ==="

# 检查依赖
echo "检查依赖..."
python3 --version >/dev/null 2>&1 || { echo "需要 Python3"; exit 1; }

# 创建虚拟环境
echo "创建 Python 虚拟环境..."
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -q requests curlify 2>/dev/null || true

echo "=== 基础环境就绪 ==="
echo ""
echo "下一步: 配置 ListenHub API Key"
echo "请提供你的 ListenHub API Key，我将创建配置文件"
