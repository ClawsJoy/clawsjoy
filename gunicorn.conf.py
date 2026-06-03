"""Gunicorn 配置文件 - 内存优化版"""

import os
import sys

chdir = "/home/flybo/clawsjoy_v5"

raw_env = [f"PYTHONPATH={chdir}"]

# 减少 workers 避免内存不足
workers = 2
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

# 内存限制（单位：字节）
max_requests = 500
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


def worker_exit(server, worker):
    try:
        from core.lib.config_watcher import config_watcher

        config_watcher.stop()
    except:
        pass
    print(f"🛑 Worker {worker.pid} 已停止")


def on_starting(server):
    print("🚀 ClawsJoy Gateway 启动中...")


def when_ready(server):
    print(f"✅ ClawsJoy Gateway 已就绪 (PID: {server.pid})")


def on_exit(server):
    print("👋 ClawsJoy Gateway 已停止")
