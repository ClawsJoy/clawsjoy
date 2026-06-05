"""Gunicorn 配置文件 - 生产优化版"""

import multiprocessing
import os

chdir = "/home/flybo/clawsjoy_v5"
raw_env = [f"PYTHONPATH={chdir}"]

# 根据 CPU 核心数动态调整
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
threads = 4
worker_class = "gthread"

bind = "0.0.0.0:5002"

accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

daemon = False
proc_name = "clawsjoy-gateway"

timeout = 120
graceful_timeout = 30
keepalive = 5

# 内存保护
max_requests = 1000
max_requests_jitter = 50


def post_fork(server, worker):
    import sys

    sys.path.insert(0, "/home/flybo/clawsjoy_v5")
    try:
        from core.lib.config_auto_watcher import config_auto_watcher

        config_auto_watcher.scan_and_register()
        config_auto_watcher.start()
        print(f"✅ Worker {worker.pid} 配置监听器已启动")
    except Exception as e:
        print(f"⚠️ Worker {worker.pid} 监听器启动失败: {e}")


def on_starting(server):
    print("🚀 ClawsJoy Gateway 启动中...")


def when_ready(server):
    print(f"✅ ClawsJoy Gateway 已就绪 (PID: {server.pid})")
