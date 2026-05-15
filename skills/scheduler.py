"""定时任务调度器 - 自动化执行"""
import threading
import time
import json
from datetime import datetime
from pathlib import Path

class TaskSchedulerSkill:
    name = "scheduler"
    description = "定时任务调度器"
    version = "1.0.0"
    category = "core"
    
    def __init__(self):
        self.tasks = {}
        self.running = True
        self._load_tasks()
    
    def _load_tasks(self):
        task_file = Path("data/scheduled_tasks.json")
        if task_file.exists():
            with open(task_file, 'r') as f:
                self.tasks = json.load(f)
    
    def _save_tasks(self):
        task_file = Path("data/scheduled_tasks.json")
        task_file.parent.mkdir(parents=True, exist_ok=True)
        with open(task_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, name, schedule_time, task_type, params=None):
        """添加定时任务"""
        self.tasks[name] = {
            "name": name,
            "schedule": schedule_time,
            "type": task_type,
            "params": params,
            "created_at": datetime.now().isoformat()
        }
        self._save_tasks()
        return {"success": True, "message": f"任务 {name} 已添加"}
    
    def list_tasks(self):
        return list(self.tasks.keys())
    
    def remove_task(self, name):
        if name in self.tasks:
            del self.tasks[name]
            self._save_tasks()
            return {"success": True}
        return {"success": False, "error": "任务不存在"}
    
    def execute(self, params):
        operation = params.get("operation", "list")
        if operation == "add":
            return self.add_task(
                params.get("name"),
                params.get("schedule"),
                params.get("type", "skill"),
                params.get("params")
            )
        elif operation == "list":
            return {"tasks": self.list_tasks()}
        elif operation == "remove":
            return self.remove_task(params.get("name"))
        return {"success": False, "error": "未知操作"}

scheduler = TaskSchedulerSkill()
