"""可靠调度器 - 定时任务管理"""

import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable


class ReliableScheduler:
    """可靠调度器"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.thread = None
        self._load_tasks()
    
    def _load_tasks(self):
        """加载任务配置"""
        config_file = Path("config/scheduler.yaml")
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.tasks = config.get('tasks', {})
    
    def register_task(self, name: str, schedule: str, command: str, enabled: bool = True):
        """注册定时任务"""
        self.tasks[name] = {
            'schedule': schedule,
            'command': command,
            'enabled': enabled,
            'last_run': None,
            'next_run': None
        }
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("✅ 调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
    
    def _run(self):
        """主循环"""
        while self.running:
            now = datetime.now()
            
            for name, task in self.tasks.items():
                if not task.get('enabled', True):
                    continue
                
                schedule = task.get('schedule', '')
                if self._should_run(schedule, now, task.get('last_run')):
                    self._execute_task(name, task)
                    task['last_run'] = now
            
            time.sleep(60)  # 每分钟检查一次
    
    def _should_run(self, schedule: str, now: datetime, last_run) -> bool:
        """判断是否应该执行"""
        # 简单实现：支持分钟级调度
        if schedule.startswith('*/'):
            interval = int(schedule[2:])
            if last_run is None:
                return True
            minutes_since = (now - last_run).total_seconds() / 60
            return minutes_since >= interval
        
        # 支持 cron 格式简化版
        parts = schedule.split()
        if len(parts) >= 2:
            minute = parts[0]
            hour = parts[1] if len(parts) > 1 else '*'
            
            if minute != '*' and int(minute) != now.minute:
                return False
            if hour != '*' and int(hour) != now.hour:
                return False
            return True
        
        return False
    
    def _execute_task(self, name: str, task: Dict):
        """执行任务"""
        print(f"[{datetime.now()}] 执行任务: {name}")
        command = task.get('command', '')
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"  ✅ {name} 成功")
            else:
                print(f"  ❌ {name} 失败: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {name} 超时")
        except Exception as e:
            print(f"  ❌ {name} 错误: {e}")


# 全局调度器
scheduler = ReliableScheduler()
