#!/bin/bash

cd /app/bin

# 启动所有 API
python3 auth_api.py &
python3 tenant_api.py &
python3 billing_api.py &
python3 promo_api.py &
python3 coffee_api.py &
python3 message_router.py &
python3 redis_queue.py &
python3 task_api.py &
python3 joymate_api.py &

# 启动 Web 服务（关键：绑定到 0.0.0.0）
cd /app/web
python3 -m http.server 8082 --bind 0.0.0.0 &

# 等待所有进程
wait
python3 chat_api_agent.py &
