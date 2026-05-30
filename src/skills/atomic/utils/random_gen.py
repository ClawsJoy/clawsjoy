#!/usr/bin/env python3
"""Random Gen - Random Gen 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""随机数生成器"""
import random
import string

class RandomGenSkill:
    name = "random_gen"
    description = "生成随机数或随机字符串"
    version = "1.0.0"
    category = "utils"
    
    def execute(self, params):
        type = params.get("type", "int")
        
        if type == "int":
            min_val = params.get("min", 0)
            max_val = params.get("max", 100)
            result = random.randint(min_val, max_val)
        elif type == "float":
            min_val = params.get("min", 0.0)
            max_val = params.get("max", 1.0)
            result = random.uniform(min_val, max_val)
        elif type == "string":
            length = params.get("length", 10)
            chars = string.ascii_letters + string.digits
            result = ''.join(random.choices(chars, k=length))
        else:
            result = random.random()
        
        return {"success": True, "result": result, "type": type}

skill = RandomGenSkill()
