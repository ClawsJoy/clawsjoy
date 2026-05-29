#!/bin/bash

echo "========================================="
echo "ClawsJoy API 测试"
echo "========================================="

# 1. 测试 Ollama
echo ""
echo "📍 1. 测试 Ollama 服务"
curl -s http://localhost:11434/api/tags | head -c 200
echo ""

# 2. 测试健康检查
echo ""
echo "📍 2. 测试健康检查 API"
curl -s http://localhost:5002/api/health | python3 -m json.tool 2>/dev/null || echo "API 未响应"

# 3. 测试技能推荐
echo ""
echo "📍 3. 测试技能推荐 API"
curl -s -X POST http://localhost:5002/api/skills/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "学习中文", "n": 3}' | python3 -m json.tool 2>/dev/null

# 4. 测试技能市场列表
echo ""
echo "📍 4. 测试技能市场列表"
curl -s http://localhost:5002/api/skill-market/list | python3 -m json.tool 2>/dev/null | head -30

echo ""
echo "========================================="
echo "测试完成"
echo "========================================="
