#!/bin/bash
# 让 Agent 在实际问题中学习

echo "🧠 Agent 实战学习开始..."

# 1. 模拟服务故障让 Agent 学习
echo "📚 学习内容1: 服务恢复"
python3 -c "
from agents.engineer_agent import EngineerAgent
e = EngineerAgent()
e.learn_service_recovery()
print('✅ 服务恢复已学习')
"

# 2. 学习连接池问题
echo "📚 学习内容2: 连接池优化"
python3 -c "
from agents.engineer_agent import EngineerAgent
e = EngineerAgent()
e.learn_connection_pool()
print('✅ 连接池优化已学习')
"

# 3. 从历史错误中学习
echo "📚 学习内容3: 错误模式识别"
python3 -c "
from agents.engineer_agent import EngineerAgent
e = EngineerAgent()
e.learn_from_recent_errors()
print('✅ 错误模式已学习')
"

echo ""
echo "=== Agent 已学会的知识 ==="
cat data/system_status.json 2>/dev/null | grep -A10 "learned_fixes" || echo "暂无学习记录"
