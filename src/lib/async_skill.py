from lib.smart_config import smart_config
"""异步技能执行器 - 长耗时任务异步执行"""
import threading
import uuid
from datetime import datetime
from typing import Dict, Any

class AsyncSkillExecutor:
    """异步技能执行器"""
    
    _instance = None
    _tasks: Dict[str, Dict] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def submit(self, skill_name: str, params: Dict) -> str:
        """提交异步任务"""
        task_id = str(uuid.uuid4())[:8]
        
        def run():
            try:
                from src.api.gateway import _skills
                if skill_name in _skills:
                    result = _skills[skill_name].execute(params)
                    self._tasks[task_id] = {
                        "status": "completed",
                        "result": result,
                        "completed_at": datetime.now().isoformat()
                    }
                else:
                    self._tasks[task_id] = {
                        "status": "failed",
                        "error": f"技能不存在: {skill_name}"
                    }
            except Exception as e:
                self._tasks[task_id] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        self._tasks[task_id] = {"status": "pending", "submitted_at": datetime.now().isoformat()}
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
        return task_id
    
    def get_result(self, task_id: str) -> Dict:
        """获取任务结果"""
        return self._tasks.get(task_id, {"status": "not_found"})
    
    def list_tasks(self) -> Dict:
        """列出所有任务"""
        return self._tasks

async_executor = AsyncSkillExecutor()
