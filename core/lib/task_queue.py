#!/usr/bin/env python3
"""Task Queue - Task Queue 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""任务队列引擎 v1.0.1 - 支持持久化"""

import json
import time
from datetime import datetime
from collections import deque
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List
from core.lib.memory_simple import memory

class Priority(Enum):
    EMERGENCY = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    EXPLORE = 4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"

class Task:
    def __init__(self, task_id: str, name: str, skill: str, params: dict,
                 priority: Priority = Priority.NORMAL, source: str = "system"):
        self.id = task_id
        self.name = name
        self.skill = skill
        self.params = params
        self.priority = priority
        self.source = source
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.retry_count = 0
        self.max_retry = 3
        self.result = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "skill": self.skill,
            "params": self.params,
            "priority": self.priority.name,
            "source": self.source,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "retry_count": self.retry_count,
            "result": self.result
        }


class TaskQueue:
    def __init__(self, persist_file=f"{get_data_root()}/task_history.json"):
        self.persist_file = Path(persist_file)
        self.pending: List[Task] = []
        self.running: Optional[Task] = None
        self.completed: List[Task] = []
        self.abandoned: List[Task] = []
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        if self.persist_file.exists():
            with open(self.persist_file, 'r') as f:
                data = json.load(f)
                # 只恢复统计，不恢复待处理任务
                self._stats = data.get("stats", {"completed": 0, "abandoned": 0})
        else:
            self._stats = {"completed": 0, "abandoned": 0}
    
    def _save_history(self):
        """保存历史记录"""
        data = {
            "stats": self._stats,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.persist_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add(self, task: Task) -> bool:
        for t in self.pending:
            if t.name == task.name and t.skill == task.skill:
                return False
        self.pending.append(task)
        self._sort()
        return True
    
    def _sort(self):
        self.pending.sort(key=lambda t: (t.priority.value, -t.retry_count))
    
    def pop_next(self) -> Optional[Task]:
        if not self.pending:
            return None
        return self.pending.pop(0)
    
    def complete(self, task: Task, result: dict):
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result
        self.completed.append(task)
        self._stats["completed"] += 1
        self._save_history()
        self.running = None

        # 写入记忆
        memory.remember(
            f"任务完成|{task.name}|技能:{task.skill}|时间:{task.completed_at}",
            category="task_history"
        )
    
    def fail(self, task: Task, error: str):
        task.retry_count += 1
        if task.retry_count >= task.max_retry:
            self.abandon(task, f"重试{task.max_retry}次失败: {error}")
        else:
            task.status = TaskStatus.PENDING
            self.pending.append(task)
            self._sort()
    
    def abandon(self, task: Task, reason: str):
        task.status = TaskStatus.ABANDONED
        task.completed_at = datetime.now().isoformat()
        task.result = {"error": reason}
        self.abandoned.append(task)
        self._stats["abandoned"] += 1
        self._save_history()
        self.running = None

        memory.remember(
            f"任务放弃|{task.name}|原因:{reason}",
            category="abandoned_tasks"
        )
    
    def start(self, task: Task):
        task.status = TaskStatus.RUNNING
        self.running = task
    
    def get_status(self) -> dict:
        return {
            "pending": len(self.pending),
            "running": self.running.to_dict() if self.running else None,
            "completed": self._stats["completed"],
            "abandoned": self._stats["abandoned"]
        }
    
    def get_recent_completed(self, limit: int = 10) -> List[dict]:
        return [t.to_dict() for t in self.completed[-limit:]]
    
    def get_recent_abandoned(self, limit: int = 10) -> List[dict]:
        return [t.to_dict() for t in self.abandoned[-limit:]]

task_queue = TaskQueue()

# 添加到 TaskQueue 类中

def adjust_priority(self, task_id: str, new_priority: Priority):
    """动态调整任务优先级"""
    for task in self.pending:
        if task.id == task_id:
            task.priority = new_priority
            self._sort()
            return True
    return False

def promote_by_wait_time(self, max_wait_seconds: int = 300):
    """等待超过时间的任务提升优先级"""
    now = datetime.now()
    for task in self.pending:
        created = datetime.fromisoformat(task.created_at)
        wait_seconds = (now - created).total_seconds()
        if wait_seconds > max_wait_seconds and task.priority.value > 1:
            old_priority = task.priority.name
            task.priority = Priority(task.priority.value - 1)
            self._sort()
            print(f"  📈 任务 {task.name} 优先级提升: {old_priority} -> {task.priority.name}")
