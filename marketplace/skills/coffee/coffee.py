"""咖啡订购和店铺查询技能 - 标准格式"""

from typing import Dict
from skills.skill_interface import BaseSkill
import sys
import json
import importlib.util

class CoffeeSkill(BaseSkill):
    name = "coffee"
    description = "咖啡订购和店铺查询"
    version = "1.0.0"
    category = "api"
    
    def _load_original(self):
        """加载原始 execute 函数"""
        try:
            spec = importlib.util.spec_from_file_location(
                "coffee_module", 
                "skills/coffee/execute.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.execute
        except Exception as e:
            print(f"加载 coffee 失败: {e}")
            return None
    
    def execute(self, params: Dict) -> Dict:
        execute_func = self._load_original()
        if execute_func:
            return execute_func(params)
        return {"error": "Failed to load skill"}

skill = CoffeeSkill()
