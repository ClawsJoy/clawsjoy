#!/bin/bash
# 关键词学习器专属学习

echo "📚 关键词学习器学习语义..."
# 采集用户对话中的新词
tail -100 /mnt/d/clawsjoy/logs/chat-api-out.log | grep "📝 发现新候选词" > /tmp/new_words.txt

python3 -c "
from agents.keyword_learner import KeywordLearner
learner = KeywordLearner()
# 分析新词模式
learner.analyze_patterns()
"
