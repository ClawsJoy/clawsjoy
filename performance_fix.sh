#!/bin/bash
echo "🚀 ClawsJoy v5 性能优化"

# 1. 优化 Gunicorn 配置（减少内存压力）
cat > gunicorn.conf.py << 'GUNICORN'
"""性能优化配置"""

import multiprocessing

# 减少 worker 数量
workers = 2
threads = 2
worker_class = 'gthread'

bind = '0.0.0.0:5002'

# 超时配置
timeout = 60
graceful_timeout = 30

# 内存保护
max_requests = 500
max_requests_jitter = 50

# 日志
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

def post_fork(server, worker):
    import sys
    sys.path.insert(0, '/home/flybo/clawsjoy_v5')
    try:
        from core.lib.config_auto_watcher import config_auto_watcher
        config_auto_watcher.scan_and_register()
        config_auto_watcher.start()
    except:
        pass
GUNICORN

echo "✅ Gunicorn 配置已优化"

# 2. 重启服务
pkill -f gunicorn
sleep 2
./start_prod.sh

echo "✅ 服务已重启"
