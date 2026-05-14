"""自愈系统技能 - 标准格式"""

from typing import Dict
from skills.skill_interface import BaseSkill
import sys
import json
import importlib.util

class SelfHealSkill(BaseSkill):
    name = "self_heal"
    description = "自愈系统"
    version = "1.0.0"
    category = "ops"
    
    def _load_original(self):
        """加载原始 execute 函数"""
        try:
            spec = importlib.util.spec_from_file_location(
                "self_heal_module", 
                "skills/self_heal/execute.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.execute
        except Exception as e:
            print(f"加载 self_heal 失败: {e}")
            return None
    
    def execute(self, params: Dict) -> Dict:
        execute_func = self._load_original()
        if execute_func:
            return execute_func(params)
        return {"error": "Failed to load skill"}

skill = SelfHealSkill()
