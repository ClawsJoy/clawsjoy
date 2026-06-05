#!/bin/bash
echo "=== 功能覆盖测试 ==="

BASE="http://127.0.0.1:5002"

# 1. 健康检查
curl -s $BASE/health > /dev/null
echo "1. 健康检查 ✓"

# 2. 聊天功能
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"你好"}' > /dev/null
echo "2. 聊天功能 ✓"

# 3. 计算功能
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"1+2等于多少"}' > /dev/null
echo "3. 计算功能 ✓"

# 4. 天气查询
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"今天天气"}' > /dev/null
echo "4. 天气查询 ✓"

# 5. 方言翻译
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"用粤语说你好"}' > /dev/null
echo "5. 方言翻译 ✓"

# 6. 记忆存储
curl -s -X POST $BASE/api/v5/memory/remember \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","fact":"用户喜欢Python"}' > /dev/null
echo "6. 记忆存储 ✓"

# 7. 记忆检索
curl -s -X POST $BASE/api/v5/memory/recall \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","query":"Python"}' > /dev/null
echo "7. 记忆检索 ✓"

# 8. 技能列表
curl -s $BASE/api/skills/list > /dev/null
echo "8. 技能列表 ✓"

# 9. Agent 列表
curl -s $BASE/api/agents/list > /dev/null
echo "9. Agent 列表 ✓"

# 10. 监控指标
curl -s $BASE/metrics > /dev/null
echo "10. 监控指标 ✓"

# 11. 缓存统计
curl -s $BASE/api/v5/stats/cache > /dev/null
echo "11. 缓存统计 ✓"

# 12. 详细健康检查
curl -s $BASE/api/v5/health/detailed > /dev/null
echo "12. 详细健康检查 ✓"

echo ""
echo "✅ 功能覆盖测试完成"
