#!/bin/bash
# 提交 GPU 临时任务

TASK_NAME="$1"
TASK_CMD="$2"

if [ -z "$TASK_NAME" ] || [ -z "$TASK_CMD" ]; then
    echo "用法: $0 <任务名> <命令>"
    echo "示例: $0 video 'curl -X POST http://localhost:8105/api/promo/make'"
    exit 1
fi

cd /mnt/d/clawsjoy

# 提交到 GPU 队列
python3 -c "
import json
from pathlib import Path
import time

TASKS_DIR = Path('/mnt/d/clawsjoy/tasks')
task = {
    'name': '$TASK_NAME',
    'cmd': '$TASK_CMD',
    'submitted': '$(date -Iseconds)',
    'priority': 5
}
queue_file = TASKS_DIR / f'gpu_queue_{int(time.time())}.json'
with open(queue_file, 'w') as f:
    json.dump(task, f)
print(f'✅ GPU 任务已提交: $TASK_NAME')
"
