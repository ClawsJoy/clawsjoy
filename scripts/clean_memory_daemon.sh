#!/bin/bash
while true; do
    # 每周日执行（检查星期几）
    if [ $(date +%u) -eq 7 ]; then
        cd /mnt/d/clawsjoy && ./scripts/clean_memory.sh >> logs/clean_memory.log 2>&1
        sleep 86400  # 等待一天
    fi
    sleep 3600  # 每小时检查一次
done
