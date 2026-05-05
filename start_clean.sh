#!/bin/bash
cd /mnt/d/clawsjoy/bin

echo "启动认证服务 (8092)..."
python3 auth_api.py > /tmp/auth.log 2>&1 &

sleep 1
echo "启动租户服务 (8088)..."
python3 tenant_api.py > /tmp/tenant.log 2>&1 &

sleep 1
echo "启动计费服务 (8090)..."
python3 billing_api.py > /tmp/billing.log 2>&1 &

sleep 1
echo "启动宣传片服务 (8086)..."
python3 promo_api.py > /tmp/promo.log 2>&1 &

sleep 1
echo "启动咖啡服务 (8085)..."
python3 coffee_api.py > /tmp/coffee.log 2>&1 &

sleep 1
echo "启动任务调度器 (8084)..."
python3 task_api.py > /tmp/task.log 2>&1 &

sleep 2
echo "启动 Web 服务 (8082)..."
cd ../web
python3 -m http.server 8082 > /tmp/web.log 2>&1 &

echo ""
echo "✅ 服务已启动"
echo ""
echo "查看日志: tail -f /tmp/*.log"
