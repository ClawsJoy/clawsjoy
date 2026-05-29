"""智能主动服务 - 简化版"""

from datetime import datetime
from typing import Dict


class SmartActiveService:
    """智能主动服务"""

    def __init__(self):
        print("💡 智能主动服务已启动")

    def on_task_complete(self, agent: str, user_id: str, task: str, data: Dict):
        """任务完成时触发"""
        print(f"🎯 [主动服务] {agent} 完成任务: {task}")

    def on_error(self, agent: str, user_id: str, error: str):
        """错误时触发"""
        print(f"🚨 [主动服务] {agent} 发生错误: {error}")

    def should_serve(self, agent: str, context: Dict) -> Dict:
        return {"should": False, "reason": "", "priority": 0}


smart_service = SmartActiveService()
