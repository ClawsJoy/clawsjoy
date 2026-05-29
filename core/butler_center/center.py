"""管家中心 - 调度和管理所有管家服务"""

from typing import Dict, Optional, List
from pathlib import Path
import json
from datetime import datetime


class ButlerCenter:
    """管家中心 - 统一调度"""

    def __init__(self):
        self.butlers: Dict[str, Dict] = {}
        self.task_queue: List[Dict] = []
        self._load_butlers()

    def _load_butlers(self):
        """加载已注册的管家"""
        butler_types = ["personal_butler_v2", "fixed_butler", "memory_driven_butler", "voice_butler"]
        for bt in butler_types:
            self.butlers[bt] = {
                "name": bt,
                "status": "active",
                "registered_at": datetime.now().isoformat()
            }

    def register_butler(self, butler_name: str, metadata: Dict = None) -> bool:
        """注册管家"""
        self.butlers[butler_name] = {
            "name": butler_name,
            "metadata": metadata or {},
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        return True

    def get_butler(self, butler_name: str) -> Optional[Dict]:
        """获取管家信息"""
        return self.butlers.get(butler_name)

    def list_butlers(self) -> List[str]:
        """列出所有管家"""
        return list(self.butlers.keys())

    def get_active_butlers(self) -> List[Dict]:
        """获取活跃管家"""
        return [b for b in self.butlers.values() if b.get("status") == "active"]

    def dispatch_task(self, task: Dict, butler_name: str = None) -> Dict:
        """分发任务到管家"""
        if butler_name and butler_name in self.butlers:
            target = butler_name
        else:
            target = "personal_butler_v2"  # 默认管家
        
        return {
            "task": task,
            "target": target,
            "status": "dispatched",
            "timestamp": datetime.now().isoformat()
        }

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_butlers": len(self.butlers),
            "active_butlers": len(self.get_active_butlers()),
            "queue_size": len(self.task_queue),
            "butlers": list(self.butlers.keys())
        }


# 全局实例
butler_center = ButlerCenter()
