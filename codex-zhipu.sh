#!/bin/bash
# Codex 启动脚本 - 使用智谱 API 中转

export OPENAI_BASE_URL="https://open.bigmodel.cn/api/openai"
export OPENAI_API_KEY="acbf98792d5d49aa89d5070ea6c9ddbe.WEifERHJGOuZUiJ9"

# 运行 Codex
codex "$@"
