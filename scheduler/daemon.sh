#!/bin/bash
cd /mnt/d/clawsjoy
while true; do
    if ! pgrep -f "reliable_scheduler.py" > /dev/null; then
        echo "$(date): 启动调度器" >> logs/daemon.log
        nohup python3 scheduler/reliable_scheduler.py >> logs/scheduler.log 2>&1 &
    fi
    sleep 30
done
