#!/bin/bash
echo "🦞 核心 Agent 学习报告"

echo -e "\n📚 关键词学习:"
python3 -c "
from agents.keyword_learner import KeywordLearner
k = KeywordLearner()
print(f'  关键词库: {len(k._get_existing_keywords())} 个')
"

echo -e "\n🕷️ 采集学习:"
echo "  发现 URL: $(cat data/urls/discovered.json 2>/dev/null | wc -l) 个"

echo -e "\n🔧 工程师学习:"
echo "  修复记录: $(grep -c '✅' logs/engineer.log 2>/dev/null || echo 0) 次"

echo -e "\n✅ 核心 Agent 学习完成"
