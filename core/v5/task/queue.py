#!/usr/bin/env python3
"""Queue - Queue 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import queue
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict


class Task:
    """任务"""

    def __init__(
        self, name: str, func: Callable, args: tuple = None, kwargs: dict = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None


class TaskQueue:
    """任务队列"""

    def __init__(self, workers: int = 2):
        self.queue = queue.Queue()
        self.tasks: Dict[str, Task] = {}
        self.workers = workers
        self._running = False
        self._threads = []

    def submit(self, name: str, func: Callable, *args, **kwargs) -> str:
        """提交任务"""
        task = Task(name, func, args, kwargs)
        self.tasks[task.id] = task
        self.queue.put(task)
        return task.id

    def get_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return {"status": "not_found"}
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "result": task.result,
            "error": str(task.error) if task.error else None,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
        }

    def start(self):
        """启动 workers"""
        self._running = True
        for i in range(self.workers):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self._threads.append(thread)
        print(f"   ✅ 任务队列已启动 (workers: {self.workers})")

    def _worker(self):
        """工作线程"""
        while self._running:
            try:
                task = self.queue.get(timeout=1)
                task.status = "running"
                try:
                    result = task.func(*task.args, **task.kwargs)
                    task.result = result
                    task.status = "completed"
                except Exception as e:
                    task.error = e
                    task.status = "failed"
                task.completed_at = datetime.now().isoformat()
            except queue.Empty:
                continue

    def stop(self):
        """停止"""
        self._running = False
        for thread in self._threads:
            thread.join(timeout=2)


task_queue = TaskQueue()
