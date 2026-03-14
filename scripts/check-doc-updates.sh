#!/bin/bash
#
# OpenClaw 文档更新检测脚本
# 每天早上检查两份官方文档是否有更新
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/root/.openclaw/workspace"
KNOWLEDGE_DIR="$WORKSPACE_DIR/knowledge"
LOG_FILE="$WORKSPACE_DIR/.doc-update.log"
NOTIFY_FILE="$WORKSPACE_DIR/.doc-update-notify"

# 文档配置
DOC1_URL="https://docs.openclaw.ai/zh-CN/concepts/multi-agent"
DOC1_LOCAL="$KNOWLEDGE_DIR/openclaw-multi-agent.md"
DOC1_NAME="多智能体路由文档"

DOC2_URL="https://raw.githubusercontent.com/openclaw/openclaw/main/README.md"
DOC2_LOCAL="$KNOWLEDGE_DIR/openclaw-github-readme.md"
DOC2_NAME="GitHub README"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取远程文档内容
fetch_doc() {
    local url="$1"
    local output="$2"
    
    if [[ "$url" == *"raw.githubusercontent.com"* ]]; then
        # GitHub raw 使用 curl
        curl -fsSL "$url" -o "$output" 2>/dev/null || return 1
    else
        # 其他使用 wget
        wget -q "$url" -O "$output" 2>/dev/null || return 1
    fi
}

# 计算文件哈希
get_hash() {
    md5sum "$1" 2>/dev/null | awk '{print $1}' || echo ""
}

# 检测单个文档更新
check_update() {
    local url="$1"
    local local_file="$2"
    local doc_name="$3"
    local temp_file="/tmp/doc_check_$(basename "$local_file").tmp"
    
    log "检查 $doc_name..."
    
    # 获取远程内容
    if ! fetch_doc "$url" "$temp_file"; then
        log "  ✗ 无法获取远程文档: $doc_name"
        return 1
    fi
    
    # 如果本地文件不存在，直接保存
    if [[ ! -f "$local_file" ]]; then
        log "  → 本地文件不存在，首次保存"
        cp "$temp_file" "$local_file"
        echo "$doc_name: 首次同步" >> "$NOTIFY_FILE"
        rm -f "$temp_file"
        return 0
    fi
    
    # 对比哈希
    local remote_hash=$(get_hash "$temp_file")
    local local_hash=$(get_hash "$local_file")
    
    if [[ "$remote_hash" != "$local_hash" ]]; then
        log "  ✓ 检测到更新: $doc_name"
        
        # 保存旧版本用于生成diff
        local backup_file="${local_file}.bak"
        cp "$local_file" "$backup_file"
        
        # 更新本地文件
        cp "$temp_file" "$local_file"
        
        # 生成变更摘要（前10行差异）
        local diff_summary=$(diff -u "$backup_file" "$local_file" 2>/dev/null | head -30 || echo "文件有更新")
        
        # 统计变更行数
        local add_lines=$(echo "$diff_summary" | grep -c "^+" 2>/dev/null || echo "0")
        local del_lines=$(echo "$diff_summary" | grep -c "^-" 2>/dev/null || echo "0")
        
        echo "$doc_name: 有更新 (+$add_lines -$del_lines 行)" >> "$NOTIFY_FILE"
        
        # 清理备份
        rm -f "$backup_file"
        rm -f "$temp_file"
        return 0
    else
        log "  → 无更新"
        rm -f "$temp_file"
        return 1
    fi
}

# 主流程
main() {
    log "=== 文档更新检测开始 ==="
    
    # 清空通知文件
    > "$NOTIFY_FILE"
    
    local has_update=false
    
    # 检查文档1
    if check_update "$DOC1_URL" "$DOC1_LOCAL" "$DOC1_NAME"; then
        has_update=true
    fi
    
    # 检查文档2
    if check_update "$DOC2_URL" "$DOC2_LOCAL" "$DOC2_NAME"; then
        has_update=true
    fi
    
    # 如果有更新，输出通知内容
    if [[ "$has_update" == "true" ]]; then
        log "=== 发现更新，准备通知 ==="
        cat "$NOTIFY_FILE"
        exit 0
    else
        log "=== 所有文档均为最新 ==="
        exit 1
    fi
}

main "$@"
