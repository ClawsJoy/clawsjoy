#!/bin/bash
# 根据用户输入匹配并执行 Skill

QUERY="$1"
if [ -z "$QUERY" ]; then
    echo "用法: skill_executor.sh <用户问题>"
    exit 1
fi

# 关键词匹配
if echo "$QUERY" | grep -qi "宣传片\|香港\|科技"; then
    echo "🎬 匹配到宣传片制作 Skill"
    echo "   Skill: 2026-04-28_香港科技宣传片"
    echo "   执行建议: spider_unsplash \"hongkong tech\" 5"
    echo "            make_video --style tech --color #667eea"
    exit 0
fi

if echo "$QUERY" | grep -qi "图片\|采集\|夜景"; then
    echo "📸 匹配到图片采集 Skill"
    echo "   Skill: 2026-04-27_批量图片采集"
    echo "   执行建议: spider_unsplash \"hongkong night\" 10"
    exit 0
fi

echo "未匹配到特定 Skill，使用通用处理"
