"""智能调度器 - 根据优先级和资源动态调度任务"""

import heapq
import threading
import time
from datetime import datetime
from queue import Queue
from typing import Dict, List, Any
import json
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class TaskPriority:
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

class SmartScheduler:
    def __init__(self):
        self.task_queue = []
        self.queue_lock = threading.Lock()
        self.running = True
        self.stats = {"scheduled": 0, "completed": 0, "failed": 0}
        self.schedule_file = Path("data/schedule_history.json")
        self._load_history()
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=self._run, daemon=True)
        self.scheduler_thread.start()
    
    def _load_history(self):
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                data = json.load(f)
                self.stats = data.get('stats', self.stats)
    
    def _save_history(self):
        with open(self.schedule_file, 'w') as f:
            json.dump({"stats": self.stats, "last_updated": datetime.now().isoformat()}, f, indent=2)
    
    def add_task(self, name: str, func, args=None, priority=TaskPriority.NORMAL, 
                 max_retries=3, timeout=60):
        """添加任务到队列"""
        task_id = f"{name}_{datetime.now().timestamp()}"
        task = {
            "id": task_id,
            "name": name,
            "func": func,
            "args": args or [],
            "priority": priority,
            "max_retries": max_retries,
            "retries": 0,
            "timeout": timeout,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        with self.queue_lock:
            heapq.heappush(self.task_queue, (priority, task_id, task))
        
        self.stats["scheduled"] += 1
        self._save_history()
        
        brain.record_experience(
            agent="smart_scheduler",
            action=f"添加任务: {name}",
            result={"success": True, "priority": priority},
            context="scheduling"
        )
        
        return task_id
    
    def _execute_task(self, task):
        """执行单个任务"""
        print(f"▶️ 执行: {task['name']} (优先级 {task['priority']})")
        
        try:
            # 设置超时
            result = task['func'](*task['args'])
            task['status'] = "completed"
            task['completed_at'] = datetime.now().isoformat()
            task['result'] = str(result)[:200]
            self.stats["completed"] += 1
            
            brain.record_experience(
                agent="smart_scheduler",
                action=f"完成任务: {task['name']}",
                result={"success": True},
                context="execution"
            )
            
            return True
        except Exception as e:
            task['retries'] += 1
            if task['retries'] < task['max_retries']:
                task['status'] = "retry"
                # 重新入队，降低优先级
                new_priority = min(task['priority'] + 1, TaskPriority.BACKGROUND)
                with self.queue_lock:
                    heapq.heappush(self.task_queue, (new_priority, task['id'], task))
                print(f"   🔄 重试 {task['retries']}/{task['max_retries']}")
            else:
                task['status'] = "failed"
                task['error'] = str(e)
                self.stats["failed"] += 1
                
                brain.record_experience(
                    agent="smart_scheduler",
                    action=f"任务失败: {task['name']}",
                    result={"success": False, "error": str(e)},
                    context="execution"
                )
            
            return False
    
    def _run(self):
        """调度主循环"""
        while self.running:
            task = None
            with self.queue_lock:
                if self.task_queue:
                    _, _, task = heapq.heappop(self.task_queue)
            
            if task:
                self._execute_task(task)
                self._save_history()
            else:
                time.sleep(1)
    
    def get_stats(self):
        return {
            "queue_size": len(self.task_queue),
            "stats": self.stats,
            "pending_tasks": [t[2]['name'] for t in self.task_queue[:5]]
        }
    
    def stop(self):
        self.running = False

# 全局调度器
scheduler = SmartScheduler()

if __name__ == '__main__':
    # 测试任务
    def test_task(msg):
        print(f"执行测试: {msg}")
        time.sleep(1)
        return "完成"
    
    scheduler.add_task("test", test_task, ["hello"], priority=TaskPriority.NORMAL)
    time.sleep(2)
    print("调度器统计:", scheduler.get_stats())
    scheduler.stop()
