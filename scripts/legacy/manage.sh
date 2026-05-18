#!/bin/bash
cd /mnt/d/clawsjoy

case "$1" in
    start)
        echo "🚀 启动 ClawsJoy..."
        ./start_clawsjoy.sh 2>/dev/null
        ;;
    stop)
        echo "🛑 停止服务..."
        pkill -f "agent_gateway|file_service|multi_agent|doc_generator"
        echo "✅ 已停止"
        ;;
    status)
        echo "📊 服务状态:"
        for port in 5002 5003 5005 5008; do
            if curl -s http://localhost:$port/health >/dev/null 2>&1; then
                echo "  ✅ :$port"
            else
                echo "  ❌ :$port"
            fi
        done
        ;;
    dashboard)
        ./dashboard_v2.sh
        ;;
    evolve)
        python3 intelligence/evolution_engine.py
        ;;
    report)
        python3 intelligence/report_generator.py
        ;;
    *)
        echo "用法: $0 {start|stop|status|dashboard|evolve|report}"
        ;;
esac
