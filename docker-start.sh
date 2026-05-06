#!/bin/bash

cd /app/bin

# 启动所有 API（每个服务独立运行，不等待）
python3 auth_api.py &
python3 tenant_api.py &
python3 billing_api.py &
python3 promo_api.py &
python3 coffee_api.py &
python3 message_router.py &
python3 redis_queue.py &
python3 task_api.py &
python3 joymate_api.py &
python3 chat_api_agent.py &
#python3 swagger_api.py &
#python3 metrics_api.py &
#python3 workflow_api.py &

# 启动 Web 服务
cd /app/web
python3 -m http.server 8082 --bind 0.0.0.0 &

# 等待所有进程
wait
