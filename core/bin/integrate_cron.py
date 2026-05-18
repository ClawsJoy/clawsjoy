#!/usr/bin/env python3
"""将现有定时任务集成到主动跑引擎"""

import sys
sys.path.insert(0, '{ROOT}')
import subprocess
from lib.task_queue import Task, Priority, task_queue

def integrate_existing_cron():
    """集成现有定时任务"""
    # 获取现有 crontab 任务
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode == 0:
        print("现有定时任务:")
        print(result.stdout[:500])
    
    # 添加为队列任务
    cron_tasks = [
        {"name": "热门爬虫", "skill": "spider", "params": {"keyword": "hot"}},
        {"name": "主题同步", "skill": "sync_topics", "params": {}},
        {"name": "健康检查", "skill": "health_check", "params": {}}
    ]
    
    for ct in cron_tasks:
        task = Task(
            task_id=f"cron_{ct['name']}",
            name=ct['name'],
            skill=ct['skill'],
            params=ct['params'],
            priority=Priority.LOW,
            source="cron_integration"
        )
        task_queue.add(task)
        print(f"✅ 已集成: {ct['name']}")

if __name__ == "__main__":
    integrate_existing_cron()
