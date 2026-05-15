#!/bin/bash
# 训练 Agent 识别新故障模式

echo "🦞 Agent 训练模式"
echo "================"

# 分析最近的错误日志
echo "📊 分析错误模式..."
grep -h "Error\|Exception\|Failed" logs/*.log 2>/dev/null | sort | uniq -c | sort -rn | head -10 > /tmp/error_patterns.txt

echo ""
echo "高频错误模式:"
cat /tmp/error_patterns.txt

echo ""
echo "建议添加以下修复方案到知识库:"
while read line; do
    count=$(echo $line | awk '{print $1}')
    error=$(echo $line | cut -d' ' -f2-)
    if [ "$count" -gt 3 ]; then
        echo "  - $error"
    fi
done < /tmp/error_patterns.txt

echo ""
echo "✅ 训练完成"
