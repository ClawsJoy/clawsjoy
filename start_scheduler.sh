#!/bin/bash
cd /mnt/d/clawsjoy
nohup python3 scheduler/smart_cron.py > logs/scheduler.log 2>&1 &
echo "调度器已启动，PID: $!"
