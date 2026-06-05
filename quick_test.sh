#!/bin/bash
echo "=== ClawsJoy v5 快速功能验证 ==="

BASE="http://127.0.0.1:5002"

# 1. 基础服务
echo -e "\n1. 健康检查:"
curl -s $BASE/health | python3 -m json.tool | head -3

# 2. 聊天功能
echo -e "\n2. 聊天测试:"
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"t1","message":"你好"}' | python3 -m json.tool | grep -E "success|response" | head -2

# 3. 计算功能
echo -e "\n3. 计算测试:"
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"t1","message":"1+2等于多少"}' | python3 -m json.tool | grep response | head -1

# 4. 缓存测试
echo -e "\n4. 缓存测试:"
echo "第一次请求..."
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"cache_test","message":"缓存测试"}' | python3 -m json.tool | grep -E "cached|agent"

echo "第二次请求..."
curl -s -X POST $BASE/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"cache_test","message":"缓存测试"}' | python3 -m json.tool | grep -E "cached|agent"

# 5. 记忆测试
echo -e "\n5. 记忆测试:"
curl -s -X POST $BASE/api/v5/memory/remember \
  -H "Content-Type: application/json" \
  -d '{"user_id":"mem_test","fact":"用户喜欢Python"}' | python3 -m json.tool | grep success

curl -s -X POST $BASE/api/v5/memory/recall \
  -H "Content-Type: application/json" \
  -d '{"user_id":"mem_test","limit":3}' | python3 -m json.tool | grep -E "success|results" | head -2

echo -e "\n✅ 验证完成"
