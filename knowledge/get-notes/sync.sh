#!/bin/bash
# Get 笔记同步助手 - 陈天式方案
# 无需 API，手动导入 + 自动处理

WORKSPACE="/root/.openclaw/workspace"
KNOWLEDGE_DIR="$WORKSPACE/knowledge/get-notes"
IMPORT_DIR="$WORKSPACE/knowledge/get-notes/import"
DATE=$(date '+%Y-%m-%d')

echo "=== Get 笔记同步助手 ==="
echo ""
echo "使用方式:"
echo "1. 在 Get 笔记中选择内容 → 导出为 Markdown/TXT"
echo "2. 将文件放入: $IMPORT_DIR/"
echo "3. 运行此脚本，自动分类整理"
echo ""

# 创建目录
mkdir -p "$IMPORT_DIR"
mkdir -p "$KNOWLEDGE_DIR"/raw
mkdir -p "$KNOWLEDGE_DIR"/by-date
mkdir -p "$KNOWLEDGE_DIR"/by-topic
mkdir -p "$KNOWLEDGE_DIR"/insights

# 检查导入文件
IMPORT_COUNT=$(ls -1 "$IMPORT_DIR" 2>/dev/null | wc -l)

if [ "$IMPORT_COUNT" -eq 0 ]; then
    echo "📂 导入目录为空: $IMPORT_DIR"
    echo ""
    echo "请先将 Get 笔记导出的文件放入此目录"
    echo "支持格式: .md .txt .html"
    exit 0
fi

echo "📥 发现 $IMPORT_COUNT 个待导入文件"
echo ""

# 处理导入文件
for file in "$IMPORT_DIR"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "处理: $filename"
        
        # 复制到原始存档
        cp "$file" "$KNOWLEDGE_DIR/raw/${DATE}_${filename}"
        
        # 按日期归档
        mkdir -p "$KNOWLEDGE_DIR/by-date/${DATE}"
        cp "$file" "$KNOWLEDGE_DIR/by-date/${DATE}/${filename}"
        
        # TODO: 自动分类（AI 分析内容主题）
        # TODO: 提取洞察（金句、观点、案例）
    fi
done

# 生成导入报告
cat > "$KNOWLEDGE_DIR/import-report-${DATE}.md" << EOF
# Get 笔记导入报告 - ${DATE}

## 导入统计
- 导入文件数: $IMPORT_COUNT
- 导入时间: $(date '+%Y-%m-%d %H:%M:%S')

## 文件清单
$(ls -1 "$KNOWLEDGE_DIR/by-date/${DATE}/" 2>/dev/null | sed 's/^/- /')

## 下一步
1. 运行 AI 分析，自动分类和提取洞察
2. 更新个人知识画像
3. 生成内容选题建议

## 待分析
$(for f in "$KNOWLEDGE_DIR/by-date/${DATE}/"*; do 
    if [ -f "$f" ]; then
        echo "- [ ] $(basename "$f")"
    fi
done)
EOF

echo ""
echo "✅ 导入完成"
echo "📊 报告: $KNOWLEDGE_DIR/import-report-${DATE}.md"
echo ""
echo "下一步: 运行 AI 分析脚本，自动分类和提取洞察"
