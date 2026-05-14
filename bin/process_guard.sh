#!/bin/bash
# 进程守护脚本

PROCESS_NAME="agent_gateway_web.py"
PROCESS_DIR="/mnt/d/clawsjoy"
LOG_FILE="/mnt/d/clawsjoy/logs/guard.log"

while true; do
    if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
        echo "[$(date)] 服务已停止，正在重启..." >> "$LOG_FILE"
        cd "$PROCESS_DIR"
        nohup python3 "$PROCESS_NAME" > logs/gateway.log 2>&1 &
        echo "[$(date)] 服务已重启" >> "$LOG_FILE"
    fi
    sleep 10
done
