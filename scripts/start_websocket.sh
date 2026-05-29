#!/bin/bash
cd /home/flybo/clawsjoy_clean

# 启动 WebSocket 服务 (端口 5003)
nohup python3 -c "
from flask import Flask
from websocket.server import socketio, register_socket_events

app = Flask(__name__)
register_socket_events()
print('WebSocket 服务启动在 http://localhost:5003')
print('测试页面: http://localhost:5003')
socketio.run(app, host='0.0.0.0', port=5003, debug=False)
" > websocket.log 2>&1 &

echo "✅ WebSocket 服务已启动 (端口 5003)"
echo "📄 测试页面: http://localhost:5003"
