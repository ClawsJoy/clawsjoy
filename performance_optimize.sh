#!/bin/bash
echo "🚀 性能优化配置"

# 1. 优化 Gunicorn 配置
cat > gunicorn.conf.py << 'GUNICORN'
"""Gunicorn 配置文件 - 性能优化版"""

import os
import multiprocessing

# 动态计算 worker 数量
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
threads = 4
worker_class = 'gthread'

bind = '0.0.0.0:5002'

# 日志
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# 性能优化
timeout = 120
graceful_timeout = 30
keepalive = 5

# 防止内存泄漏
max_requests = 1000
max_requests_jitter = 50

# 预加载应用
preload_app = True

def post_fork(server, worker):
    import sys
    sys.path.insert(0, '/home/flybo/clawsjoy_v5')
    try:
        from core.lib.config_auto_watcher import config_auto_watcher
        config_auto_watcher.scan_and_register()
        config_auto_watcher.start()
    except Exception as e:
        pass

def on_starting(server):
    print(f"🚀 ClawsJoy Gateway 启动中... Workers: {workers}")

def when_ready(server):
    print(f"✅ ClawsJoy Gateway 已就绪 (PID: {server.pid})")
GUNICORN

echo "✅ Gunicorn 配置已优化"

# 2. 优化系统限制
echo "优化系统限制..."
ulimit -n 65535

# 3. 启用 TCP 快速打开
echo "net.ipv4.tcp_fastopen = 3" | sudo tee -a /etc/sysctl.conf 2>/dev/null || echo "需要 sudo 权限"

# 4. 重启服务
echo "重启服务..."
pkill -f gunicorn
sleep 2
./start_prod.sh

echo "✅ 性能优化完成"
