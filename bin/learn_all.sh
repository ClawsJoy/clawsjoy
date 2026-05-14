#!/bin/bash
# 让所有 Agent 学习各自领域的知识

echo "🦞 Agent 集体学习开始"
echo "====================="

# 1. 工程师学习
echo "🔧 工程师学习系统运维..."
python3 agents/engineer_learner.py

# 2. 关键词学习器学习
echo "📚 关键词学习器学习语义..."
python3 agents/keyword_learner_v2.py

# 3. 爬虫学习
echo "🕷️ 爬虫学习 URL 模式..."
python3 agents/spider_learner.py

# 4. 安全 Agent 学习
echo "🔒 安全 Agent 学习敏感模式..."
python3 agents/security_learner.py

# 5. 生成学习报告
echo ""
echo "📊 学习报告:"
echo "============"
for learner in engineer_learner keyword_learner_v2 spider_learner security_learner; do
    python3 -c "
from agents.$learner import $(echo $learner | sed 's/_learner//' | sed 's/^./\u&/')Learner
l = $(echo $learner | sed 's/_learner//' | sed 's/^./\u&/')Learner()
stats = l.get_stats()
print(f\"{stats['agent']}: {stats['knowledge_count']} 条知识\")
"
done

echo ""
echo "✅ 集体学习完成"
