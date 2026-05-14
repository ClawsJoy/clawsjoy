#!/bin/bash
# OpenClaw 管理脚本

case "$1" in
    start)
        echo "🦞 启动 OpenClaw Gateway..."
        pkill -9 -f openclaw-gateway 2>/dev/null
        export OLLAMA_API_KEY="ollama-local"
        nohup openclaw gateway start --port 18789 > /tmp/openclaw_gateway.log 2>&1 &
        sleep 3
        curl -s http://localhost:18789/health && echo "✅ 启动成功" || echo "⚠️ 启动中..."
        ;;
    stop)
        echo "🦞 停止 OpenClaw Gateway..."
        pkill -9 -f openclaw-gateway
        echo "✅ 已停止"
        ;;
    status)
        if pgrep -f "openclaw-gateway" > /dev/null; then
            echo "✅ Gateway 运行中"
            ps aux | grep openclaw-gateway | grep -v grep
        else
            echo "❌ Gateway 未运行"
        fi
        ;;
    logs)
        tail -30 /tmp/openclaw_gateway.log
        ;;
    *)
        echo "用法: openclaw.sh {start|stop|status|logs}"
        ;;
esac
