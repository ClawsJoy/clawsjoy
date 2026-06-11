#!/bin/bash
# ClawsJoy v5 一键启动脚本（高并发版）

cd "$(dirname "$0")"

echo "🚀 启动 ClawsJoy v5..."

# 检查 Ollama
if ! pgrep -f "ollama" > /dev/null; then
    echo "启动 Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
fi

# 启动 LLM 服务
echo "启动 LLM 服务..."
pkill -f "llm_service_optimized" 2>/dev/null
nohup python3 scripts/llm_service_optimized.py > logs/llm.log 2>&1 &
sleep 3

# 启动网关（使用 Gunicorn 高并发）
echo "启动网关 (Gunicorn)..."
pkill -f "gunicorn.*clawsjoy" 2>/dev/null
nohup gunicorn -c gunicorn.conf.py agent_gateway_enhanced:app > logs/gunicorn.log 2>&1 &

sleep 5

# 检查服务状态
if curl -s http://localhost:5012/health > /dev/null && curl -s http://localhost:5002/health > /dev/null; then
    echo "✅ ClawsJoy v5 启动成功！"
    echo "   - 网关: http://localhost:5002 (Gunicorn 高并发)"
    echo "   - LLM服务: http://localhost:5012"
else
    echo "❌ 启动失败，请检查日志"
fi

# 预热 LLM 服务
echo "预热 LLM 服务..."
sleep 3
curl -s -X POST http://localhost:5012/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"ping"}' > /dev/null
echo "   ✅ 预热完成"
