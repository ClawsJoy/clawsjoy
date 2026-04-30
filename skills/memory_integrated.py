#!/usr/bin/env python3
"""记忆集成的 Skill 示例"""

import sys
import json
sys.path.insert(0, '/home/flybo/clawsjoy/skills')
from base_skill_stateful import StatefulSkill

class MemorySkill(StatefulSkill):
    """带记忆的 Skill"""
    
    def execute(self, params):
        action = params.get("action")
        
        # 加载记忆
        memory = self.get_state()
        last_result = memory.get("last_result", {})
        
        if action == "chat":
            prompt = params.get("prompt", "")
            
            # 记忆注入
            context = f"上次结果: {last_result}\n用户: {prompt}"
            
            result = self._call_api('POST', 'http://localhost:11434/api/generate',
                json={"model": "qwen2.5-coder:7b", "prompt": context, "stream": False})
            
            # 保存到记忆
            self.update_state({"last_result": result, "last_prompt": prompt})
            
            return result
        
        return {"error": f"Unknown action: {action}"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    skill = MemorySkill("memory_demo", tenant_id=params.get("tenant_id", "1"))
    print(json.dumps(skill.execute(params)))
