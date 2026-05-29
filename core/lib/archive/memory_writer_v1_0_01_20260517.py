from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""记忆写入器 v1.0.01 - 统一格式化写入 workflow_outcome"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from core.lib.unified_config import unified_config
from core.lib.version_manager_v1_0_01_20260517 import version_manager


class MemoryWriterV1_0_01:
    """记忆写入器 - 统一格式写入任务结果"""
    
    VERSION = "1.0.01"
    
    def __init__(self):
        self.root = unified_config.ROOT
        
    def write_task_outcome(self, task_name: str, status: str, 
                           skill: str = "", error_msg: str = "",
                           metadata: Dict = None) -> bool:
        """写入任务结果到记忆"""
        try:
            from core.lib.memory_simple import memory
            
            outcome = {
                "timestamp": datetime.now().isoformat(),
                "task": task_name,
                "status": status,
                "skill": skill,
                "version": self.VERSION
            }
            
            if error_msg:
                outcome["error"] = error_msg[:200]
            
            if metadata:
                outcome.update(metadata)
            
            memory.remember(
                json.dumps(outcome, ensure_ascii=False),
                category="workflow_outcome_v2"
            )
            
            simple_msg = f"{'✅' if status == 'success' else '❌'} {task_name}"
            memory.remember(simple_msg, category="workflow_outcome")
            
            return True
            
        except Exception as e:
            print(f"⚠️ 记忆写入失败: {e}")
            return False
    
    def write_task_success(self, task_name: str, skill: str = "", metadata: Dict = None) -> bool:
        return self.write_task_outcome(task_name, "success", skill, metadata=metadata)
    
    def write_task_failure(self, task_name: str, error_msg: str, skill: str = "", metadata: Dict = None) -> bool:
        return self.write_task_outcome(task_name, "failed", skill, error_msg, metadata)


memory_writer = MemoryWriterV1_0_01()
