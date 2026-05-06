#!/bin/bash
echo "========================================="
echo "   ClawsJoy/JoyMate 服务状态"
echo "========================================="

# PM2 状态
echo -e "\n📊 PM2 进程:"
pm2 status

# 端口监听
echo -e "\n🔌 端口监听:"
for port in 8082 8093 8101 9000; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "✅ 端口 $port - 监听中"
    else
        echo "❌ 端口 $port - 未监听"
    fi
done

# API 测试
echo -e "\n📡 API 测试:"

# Chat API
response=$(curl -s -X POST http://localhost:8101/api/agent \
  -H "Content-Type: application/json" \
  -d '{"text":"ping"}' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message', '')[:30])" 2>/dev/null)
if [ -n "$response" ]; then
    echo "✅ Chat API: $response"
else
    echo "❌ Chat API: 无响应"
fi

# Web
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/ | grep -q 200; then
    echo "✅ Web Server: 正常"
else
    echo "❌ Web Server: 异常"
fi

echo "========================================="
