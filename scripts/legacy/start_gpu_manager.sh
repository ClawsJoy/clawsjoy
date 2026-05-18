#!/bin/bash
cd /mnt/d/clawsjoy
pkill -f gpu_manager.py 2>/dev/null
nohup python3 scheduler/gpu_manager.py >> logs/gpu_manager.log 2>&1 &
echo "GPU 管理器已启动，PID: $!"
