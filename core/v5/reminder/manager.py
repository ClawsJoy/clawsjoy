"""持久化提醒管理器"""
import threading
import time
import json
import uuid
from pathlib import Path


class ReminderManager:
    """持久化提醒管理器"""
    
    def __init__(self):
        self.reminders = []
        self.running = True
        self.thread = None
        self._load()
    
    def _get_file_path(self):
        return Path(f"{config_helper.get_data_root()}/v5/reminders.json")
    
    def _load(self):
        file_path = self._get_file_path()
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    self.reminders = json.load(f)
                print(f"   📋 加载 {len(self.reminders)} 个待处理提醒")
            except:
                pass
    
    def _save(self):
        file_path = self._get_file_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        future = [r for r in self.reminders if r.get("trigger_time", 0) > time.time()]
        with open(file_path, 'w') as f:
            json.dump(future, f, indent=2)
    
    def add(self, user_id, message, seconds):
        """添加提醒"""
        reminder_id = str(uuid.uuid4())[:8]
        reminder = {
            "id": reminder_id,
            "user_id": user_id,
            "message": message,
            "trigger_time": time.time() + seconds,
            "created_at": time.time()
        }
        self.reminders.append(reminder)
        self._save()
        print(f"[提醒] 已添加: {user_id} - {seconds}秒后")
        return reminder_id
    
    def start(self):
        """启动检查线程"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("   ✅ 提醒服务已启动")
    
    def _run(self):
        while self.running:
            now = time.time()
            triggered = []
            for r in self.reminders:
                if r.get("trigger_time", 0) <= now:
                    print(f"\n🔔 提醒 [{r['user_id']}]: {r['message']}")
                    triggered.append(r)

            for r in triggered:
                self.reminders.remove(r)

            if triggered:
                self._save()

            time.sleep(1)
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


reminder_manager = ReminderManager()
