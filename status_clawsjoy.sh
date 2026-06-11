#!/bin/bash
# ClawsJoy v5 状态检查

echo "📊 ClawsJoy v5 状态"
echo "===================="

# 网关
if pgrep -f "agent_gateway_enhanced" > /dev/null; then
    echo "✅ 网关: 运行中"
    curl -s http://localhost:5002/health 2>/dev/null | python3 -m json.tool 2>/dev/null
else
    echo "❌ 网关: 未运行"
fi

echo ""

# LLM 服务
if pgrep -f "llm_service_optimized" > /dev/null; then
    echo "✅ LLM服务: 运行中"
    curl -s http://localhost:5012/health 2>/dev/null | python3 -m json.tool 2>/dev/null
else
    echo "❌ LLM服务: 未运行"
fi

echo ""

# Ollama
if pgrep -f "ollama" > /dev/null; then
    echo "✅ Ollama: 运行中"
else
    echo "⚠️ Ollama: 未运行"
fi

echo ""
echo "📈 资源使用:"
ps aux | grep -E "agent_gateway|llm_service_optimized" | grep -v grep | awk '{printf "   %s: CPU=%s%% MEM=%s%%\n", $11, $3, $4}'
