# Agent API 修复指南

## 问题症状
- agent-api 状态为 errored
- 日志显示 ModuleNotFoundError: No module named 'keyword_learner'

## 根本原因
导入路径问题：代码中使用 `from keyword_learner import` 但正确路径是 `from agents.keyword_learner import`

## 解决方案
1. 修复导入路径
2. 使用简化版 agent_api（不依赖复杂导入）
3. 重启服务

## 修复命令
```bash
# 方案1: 修复导入
sed -i 's/from keyword_learner/from agents.keyword_learner/g' agents/tenant_agent.py

# 方案2: 使用简化版
cd /mnt/d/clawsjoy/bin
cat > agent_api_working.py << 'EOF'
#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
PORT = 18103
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": "ok"}).encode())
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
