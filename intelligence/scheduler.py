"""智能调度器 - 任务优先级管理"""

import heapq
import threading
import time
from datetime import datetime
from collections import defaultdict

class IntelligentScheduler:
    def __init__(self):
        self.task_queue = []
        self.task_history = defaultdict(list)
        self.queue_lock = threading.Lock()
        self.running = True
        self._start_worker()
    
    def add_task(self, name, func, priority=5, args=None):
        """添加任务，优先级1-10（1最高）"""
        task_id = f"{name}_{datetime.now().timestamp()}"
        with self.queue_lock:
            heapq.heappush(self.task_queue, (priority, task_id, {
                "id": task_id,
                "name": name,
                "func": func,
                "args": args or [],
                "added_at": datetime.now().isoformat()
            }))
        print(f"📋 添加任务: {name} (优先级 {priority})")
        return task_id
    
    def _worker(self):
        """工作线程"""
        while self.running:
            task = None
            with self.queue_lock:
                if self.task_queue:
                    _, _, task = heapq.heappop(self.task_queue)
            
            if task:
                self._execute_task(task)
            else:
                time.sleep(0.5)
    
    def _execute_task(self, task):
        print(f"▶️ 执行: {task['name']}")
        try:
            result = task['func'](*task['args'])
            self.task_history[task['name']].append({
                "time": datetime.now().isoformat(),
                "success": True,
                "result": str(result)[:100]
            })
            print(f"   ✅ 完成")
        except Exception as e:
            self.task_history[task['name']].append({
                "time": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ 失败: {e}")
    
    def _start_worker(self):
        t = threading.Thread(target=self._worker, daemon=True)
        t.start()
    
    def get_stats(self):
        return {
            "queue_size": len(self.task_queue),
            "task_history": dict(self.task_history)
        }
    
    def stop(self):
        self.running = False

# 全局调度器
scheduler = IntelligentScheduler()

def demo_task():
    import time
    time.sleep(1)
    return "done"

if __name__ == '__main__':
    scheduler.add_task("demo", demo_task, priority=3)
    time.sleep(2)
    print(scheduler.get_stats())
    scheduler.stop()
