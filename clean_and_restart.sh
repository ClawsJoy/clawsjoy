#!/bin/bash
echo "🧹 清理所有 Gunicorn 进程..."

# 1. 杀掉所有相关进程
pkill -9 -f "gunicorn.*agent_gateway"
pkill -9 -f "gunicorn.*5002"
killall -9 gunicorn 2>/dev/null

# 2. 等待进程完全退出
sleep 3

# 3. 确认清理完成
echo "📊 剩余进程检查:"
ps aux | grep gunicorn | grep -v grep || echo "✅ 无残留进程"

# 4. 检查端口
echo "🔌 端口 5002 状态:"
netstat -tlnp | grep 5002 || echo "✅ 端口已释放"

# 5. 启动服务
echo "🚀 启动 ClawsJoy..."
cd /home/flybo/clawsjoy_v5
nohup gunicorn -c gunicorn.conf.py agent_gateway_enhanced:app > logs/gateway.log 2>&1 &

# 6. 等待启动
echo "⏳ 等待服务启动..."
sleep 5

# 7. 验证服务
echo "✅ 验证服务:"
if curl -s http://localhost:5002/health > /dev/null; then
    echo "服务运行正常:"
    curl -s http://localhost:5002/health | python3 -m json.tool
else
    echo "❌ 服务启动失败，查看日志:"
    tail -20 logs/error.log
fi

# 8. 显示进程状态
echo ""
echo "📊 当前进程:"
ps aux | grep gunicorn | grep -v grep
