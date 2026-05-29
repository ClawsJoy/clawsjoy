# 进入 V5 目录
cd /home/flybo/clawsjoy_v5

# 查看进程
ps aux | grep gunicorn | grep 5002

# 停止 V5
pkill -9 -f "gunicorn.*5002"

# 启动 V5
./start_v5.sh

# 查看日志
tail -f logs/v5_access.log
tail -f logs/v5_error.log
