"""Gunicorn 配置文件 - 生产优化版"""

import multiprocessing
import os
import sys

# 添加项目路径
sys.path.insert(0, "/home/flybo/clawsjoy_v5")

# 根据 CPU 核心数动态调整，但限制最大值
cpu_count = multiprocessing.cpu_count()
workers = min(cpu_count * 2, 8)  # 最多 8 个 worker
threads = 2  # 减少线程数
worker_class = "gthread"

bind = "0.0.0.0:5002"

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

daemon = False
proc_name = "clawsjoy-gateway"

# 超时设置
timeout = 120
graceful_timeout = 30
keepalive = 5

# 内存保护
max_requests = 1000
max_requests_jitter = 50

# 启动前钩子
def on_starting(server):
    print(f"🚀 ClawsJoy Gateway 启动中...")
    print(f"   Worker 进程: {workers}")
    print(f"   每 Worker 线程: {threads}")

def when_ready(server):
    print(f"✅ ClawsJoy Gateway 已就绪")
    print(f"   监听地址: http://0.0.0.0:5002")

def worker_exit(server, worker):
    print(f"Worker {worker.pid} 退出")
