#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 ClawsJoy 智能增强版"
echo "=========================================="

# 启动原有服务
echo "1. 启动主网关..."
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &

echo "2. 启动文件服务..."
python3 file_service_complete.py > logs/file.log 2>&1 &

echo "3. 启动多智能体..."
python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &

sleep 3

# 启动智能层（可选）
echo ""
echo "智能层选项:"
echo "  a) 监控器（推荐）"
echo "  b) 分析器"
echo "  c) 调度器"
echo "  d) 全部"
echo "  n) 不启动"
read -p "请选择 (a/b/c/d/n): " choice

case $choice in
    a)
        python3 intelligence/monitor.py > logs/monitor.log 2>&1 &
        echo "✅ 监控器已启动"
        ;;
    b)
        python3 intelligence/analyzer.py
        ;;
    c)
        python3 intelligence/scheduler.py &
        echo "✅ 调度器已启动"
        ;;
    d)
        python3 intelligence/monitor.py > logs/monitor.log 2>&1 &
        python3 intelligence/scheduler.py &
        echo "✅ 监控器和调度器已启动"
        python3 intelligence/analyzer.py
        ;;
    *)
        echo "跳过智能层"
        ;;
esac

echo ""
echo "=========================================="
echo "✅ ClawsJoy 智能增强版已启动"
echo "访问: http://localhost:5002"
echo "=========================================="
