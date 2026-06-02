"""Gunicorn 配置文件 - 解决热重载线程问题"""

import os
import sys

# 工作目录
chdir = '/home/flybo/clawsjoy_v5'

# 环境变量
raw_env = [
    f'PYTHONPATH={chdir}',
]

# Worker 配置
workers = 4
threads = 8
worker_class = 'gthread'

# 绑定地址
bind = '0.0.0.0:5002'

# 日志
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# 守护进程模式
daemon = False

# 进程名称
proc_name = 'clawsjoy-gateway'

# 超时
timeout = 120
graceful_timeout = 30


def post_fork(server, worker):
    """每个 worker fork 后执行 - 重新启动配置监听器"""
    import sys
    sys.path.insert(0, '/home/flybo/clawsjoy_v5')
    
    try:
        from core.lib.config_auto_watcher import config_auto_watcher
        # 必须先扫描注册，再启动
        config_auto_watcher.scan_and_register()
        config_auto_watcher.start()
        print(f"✅ Worker {worker.pid} 配置监听器已启动")
        
        # 验证注册状态
        from core.lib.config_watcher import config_watcher
        print(f"   Worker {worker.pid} 已注册 {len(config_watcher._callbacks)} 个文件")
    except Exception as e:
        print(f"⚠️ Worker {worker.pid} 监听器启动失败: {e}")


def worker_exit(server, worker):
    """Worker 退出前清理"""
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
