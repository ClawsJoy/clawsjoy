#!/bin/bash
cd /home/flybo/clawsjoy_v5
export PYTHONPATH=/home/flybo/clawsjoy_v5:
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434

# 启动 LLM 服务
pgrep -f llm_service > /dev/null || nohup python3 scripts/llm_service.py > logs/llm.log 2>&1 &
echo "✅ LLM 服务已启动"

# 优化后的 gunicorn 配置
# -w 8: 增加 worker 数量 (原4)
# --threads 4: 每 worker 4 线程 (原8)
# --worker-class gthread: 线程模式
# --max-requests 1000: 防止内存泄漏
# --timeout 120: 增加超时
pkill -f gunicorn
sleep 2
gunicorn -w 8 --threads 4 --worker-class gthread \
  --bind 0.0.0.0:5002 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --max-requests 1000 \
  --timeout 120 \
  --daemon \
  agent_gateway_enhanced:app

echo "✅ ClawsJoy v5 生产环境已启动 (优化版)"
echo "   网关: http://localhost:5002"
echo "   Workers: 8, Threads: 4, 并发: 32"
