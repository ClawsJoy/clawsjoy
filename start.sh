#!/bin/bash
# ClawsJoy 一键启动脚本

cd "$(dirname "$0")"

case "$1" in
    docker)
        echo "🐳 启动 Docker 版本..."
        docker-compose up -d
        echo "✅ 服务已启动"
        echo "📍 Web Dashboard: http://localhost:5011"
        ;;
    docker-ollama)
        echo "🐳 启动 Docker 版本（含 Ollama）..."
        docker-compose --profile with-ollama up -d
        echo "✅ 服务已启动"
        echo "📍 Web Dashboard: http://localhost:5011"
        ;;
    local)
        echo "🖥️ 启动本地版本..."
        python3 agent_gateway_web.py &
        python3 file_service_complete.py &
        python3 multi_agent_service_v2.py &
        python3 doc_generator.py &
        python3 agent_api.py &
        python3 web_server.py &
        echo "✅ 所有服务已启动"
        ;;
    stop)
        echo "🛑 停止所有服务..."
        docker-compose down 2>/dev/null
        pkill -f "agent_gateway_web.py\|file_service_complete.py\|multi_agent_service_v2.py\|doc_generator.py\|agent_api.py\|web_server.py"
        echo "✅ 已停止"
        ;;
    status)
        echo "📊 服务状态:"
        docker-compose ps 2>/dev/null || echo "Docker 未运行"
        echo ""
        echo "本地进程:"
        ps aux | grep -E "agent_gateway|file_service|multi_agent|doc_generator|web_server" | grep -v grep
        ;;
    *)
        echo "ClawsJoy 启动脚本"
        echo ""
        echo "用法: ./start.sh [命令]"
        echo ""
        echo "命令:"
        echo "  docker        启动 Docker 版本"
        echo "  docker-ollama 启动 Docker 版本（含 Ollama）"
        echo "  local         启动本地版本"
        echo "  stop          停止所有服务"
        echo "  status        查看服务状态"
        ;;
esac
