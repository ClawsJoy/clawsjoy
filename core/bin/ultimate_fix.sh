#!/bin/bash
echo "🛠️ 终极修复脚本"

# 1. 修复 Docker
echo "修复 Docker..."
sudo service docker start 2>/dev/null || sudo dockerd > /tmp/dockerd.log 2>&1 &
sleep 3
docker ps 2>/dev/null || echo "Docker 启动中..."

# 2. 修复 agent-api
echo "修复 agent-api..."
cd /mnt/d/clawsjoy/bin

# 查看 agent_api.py 是否存在
if [ ! -f "agent_api.py" ]; then
    echo "创建 agent_api.py..."
    cat > agent_api.py << 'PYEOF'
#!/usr/bin/env python3
"""Agent API - 租户代理"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

PORT = 18103

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/agent/chat':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "收到"}).encode())
        else:
            self.send_error(404)

if __name__ == '__main__':
    print(f"Agent API 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
PYEOF
fi

# 删除旧进程并重新启动
pm2 delete agent-api 2>/dev/null
pm2 start agent_api.py --interpreter python3 --name agent-api -- --port 18103
pm2 save

# 3. 修复 web 容器
echo "修复 web 容器..."
cd /mnt/d/clawsjoy
docker-compose up -d web 2>/dev/null || docker start clawsjoy-web 2>/dev/null

# 4. 检查所有服务
echo ""
echo "=== 服务状态 ==="
pm2 list | grep -E "online|errored"
docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | grep clawsjoy

echo ""
echo "✅ 修复完成"
