#!/bin/bash
# 启动所有 Agent 的自我学习进程

echo "🧠 启动 Agent 自我学习服务..."

# 1. 关键词学习器（后台运行）
nohup python3 -c "
from agents.keyword_learner import KeywordLearner
k = KeywordLearner()
while True:
    k.self_learn_from_logs()
    k.auto_learn()
    import time
    time.sleep(1800)  # 30分钟
" > logs/keyword_learner.log 2>&1 &
echo "✅ 关键词学习器已启动 (PID: $!)"

# 2. 爬虫学习器（后台运行）
nohup python3 -c "
from agents.url_scout import URLScout
s = URLScout()
s.load()
while True:
    s.self_learn_from_crawled()
    import time
    time.sleep(3600)  # 60分钟
" > logs/spider_learner.log 2>&1 &
echo "✅ 爬虫学习器已启动 (PID: $!)"

# 3. 工程师学习器（后台运行）
nohup python3 -c "
from agents.engineer_agent import EngineerAgent
e = EngineerAgent()
while True:
    e.self_learn_from_errors()
    e.auto_fix()
    import time
    time.sleep(600)  # 10分钟
" > logs/engineer_learner.log 2>&1 &
echo "✅ 工程师学习器已启动 (PID: $!)"

echo ""
echo "📊 查看日志:"
echo "  tail -f logs/keyword_learner.log"
echo "  tail -f logs/spider_learner.log"
echo "  tail -f logs/engineer_learner.log"
