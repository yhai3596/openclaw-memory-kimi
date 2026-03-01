#!/bin/bash
# Claude Code 启动脚本 - 使用智谱 API 中转

export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_API_KEY="acbf98792d5d49aa89d5070ea6c9ddbe.WEifERHJGOuZUiJ9"

# 运行 Claude Code
claude "$@"
