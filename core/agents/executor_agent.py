import sys; sys.path.insert(0, "/mnt/d/clawsjoy_clean")
#!/usr/bin/env python3
"""执行 Agent - 负责技能执行"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from lib.file_exchange import file_exchange
from lib.skill_registry_v4 import skill_registry


class ExecutorAgent(BaseAgent):
    """执行 Agent - 执行技能"""
    
    def __init__(self):
        super().__init__("ExecutorAgent")
        self.log(f"执行 Agent 初始化完成，可用技能: {len(skill_registry.skills)}")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理请求（实现抽象方法）"""
        return self.execute_skill("ai-image-gen", {"prompt": user_input})
    
    def execute_skill(self, skill_name: str, params: Dict) -> Dict:
        """执行技能"""
        self.log(f"执行技能: {skill_name}, 参数: {params}")
        
        if skill_name not in skill_registry.skills:
            return {"success": False, "error": f"技能 {skill_name} 不存在"}
        
        result = skill_registry.execute_skill(skill_name, params)
        return result
    
    def run(self):
        """运行主循环"""
        self.log("执行 Agent 启动，等待任务...")
        
        while True:
            message = file_exchange.receive("executor")
            if message:
                action = message.get("action")
                data = message.get("data", {})
                
                if action == "execute":
                    skill_name = data.get("skill", "ai-image-gen")
                    params = data.get("params", {"prompt": data.get("user_input", "")})
                    
                    result = self.execute_skill(skill_name, params)
                    
                    file_exchange.send(
                        to_agent="decision",
                        data={
                            "from": "executor",
                            "action": "task_complete",
                            "data": {
                                "task_id": data.get("task_id"),
                                "result": result,
                                "skill": skill_name
                            }
                        }
                    )
                    self.log(f"任务完成: {skill_name}")
            
            time.sleep(0.5)


executor_agent = ExecutorAgent()


if __name__ == "__main__":
    print("执行 Agent 测试")
    result = executor_agent.execute_skill("ai-image-gen", {"test": True})
    print(f"结果: {result}")
