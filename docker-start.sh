#!/bin/bash
# 启动 Redis
redis-server --daemonize yes

# 等待 Redis 启动
sleep 2

# 启动所有 API 服务
cd /app/bin
python3 auth_api.py &
python3 tenant_api.py &
python3 billing_api.py &
python3 promo_api.py &
python3 coffee_api.py &
python3 message_router.py &
python3 redis_queue.py &
python3 joymate_api.py &

# 启动 Web 服务
cd /app/web
python3 -m http.server 8082 &

# 等待所有后台进程
wait
