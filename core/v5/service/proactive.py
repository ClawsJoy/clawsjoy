"""主动服务系统"""

import threading
import time
from typing import Dict, List, Callable
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ScheduledTask:
    id: str
    name: str
    schedule: str
    action: Callable
    enabled: bool = True
    last_run: str = None


@dataclass
class Trigger:
    id: str
    name: str
    condition: Callable[[Dict], bool]
    action: Callable
    enabled: bool = True


class ProactiveService:
    
    def __init__(self):
        self.tasks: List[ScheduledTask] = []
        self.triggers: List[Trigger] = []
        self._running = False
        self._thread = None
    
    def add_scheduled_task(self, name: str, schedule: str, action: Callable) -> str:
        task_id = f"task_{len(self.tasks)}_{int(time.time())}"
        self.tasks.append(ScheduledTask(id=task_id, name=name, schedule=schedule, action=action))
        return task_id
    
    def add_trigger(self, name: str, condition: Callable, action: Callable) -> str:
        trigger_id = f"trigger_{len(self.triggers)}_{int(time.time())}"
        self.triggers.append(Trigger(id=trigger_id, name=name, condition=condition, action=action))
        return trigger_id
    
    def check_triggers(self, context: Dict):
        for trigger in self.triggers:
            if not trigger.enabled:
                continue
            try:
                if trigger.condition(context):
                    trigger.action(context)
            except Exception as e:
                print(f"触发器执行失败: {trigger.name}, {e}")
    
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("   ✅ 主动服务已启动")
    
    def _run(self):
        while self._running:
            current_minute = datetime.now().strftime("%H:%M")
            for task in self.tasks:
                if task.enabled and task.schedule == current_minute:
                    try:
                        task.action()
                        task.last_run = datetime.now().isoformat()
                    except Exception as e:
                        print(f"定时任务执行失败: {task.name}, {e}")
            time.sleep(60)
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)


proactive = ProactiveService()
