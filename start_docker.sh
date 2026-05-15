#!/bin/bash
cd "$(dirname "$0")"

case "$1" in
    up)
        echo "🐳 启动 Docker 容器..."
        docker-compose up -d
        echo "✅ 服务已启动"
        echo "📍 Web Dashboard: http://localhost:5011"
        echo "📍 注册中心: http://localhost:5022"
        ;;
    down)
        echo "🛑 停止 Docker 容器..."
        docker-compose down
        ;;
    logs)
        docker-compose logs -f
        ;;
    build)
        echo "🔨 重新构建镜像..."
        docker-compose build --no-cache
        ;;
    *)
        echo "用法: ./start_docker.sh {up|down|logs|build}"
        ;;
esac
