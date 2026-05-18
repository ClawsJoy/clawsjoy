#!/usr/bin/env python3
"""测试错误学习脚本"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.task_queue import task_queue
from lib.error_knowledge_v1_0_00_20260517 import error_knowledge
import uuid

# 添加测试任务
def add_test_task(name, fail_type):
    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "name": name,
        "skill": "test_fail_skill",
        "params": {"task_name": name, "fail_type": fail_type},
        "priority": 1,
        "status": "pending",
        "retry_count": 0,
        "max_retry": 3
    }
    task_queue._tasks.append(task)
    print(f"✅ 已添加测试任务: {name} (ID: {task_id})")
    return task_id

# 添加测试任务
add_test_task("[TEST] 测试连接失败任务", "connection")
add_test_task("[TEST] 测试文件未找到", "not_found")
add_test_task("[TEST] 测试超时", "timeout")

print(f"\n队列状态: 待处理={len([t for t in task_queue._tasks if t.get('status') == 'pending'])}")
