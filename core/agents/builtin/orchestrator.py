import logging
import time
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from core.agents.base.smart_agent import SmartAgent
from core.lib.workspace_manager import workspace_manager
from core.lib.smart_adapter import smart_adapter


class OrchestratorAgent(SmartAgent):
    """任务编排器 - 真正的任务分解"""

    name = "orchestrator"
    description = "任务编排与分发"
    type = "core"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.behavior = workspace_manager.get_behavior_config("orchestrator")
        print(f"[Orchestrator] 初始化完成")

    def smart_route(self, user_input: str) -> str:
        """智能路由：根据用户输入选择最合适的 Agent"""
        user_lower = user_input.lower()
        
        routing_rules = {
            "code_agent": ["代码", "编程", "python", "函数", "写一个", "实现", "排序", "算法"],
            "analysis_agent": ["分析", "统计", "趋势", "报告", "总结", "销售", "数据"],
            "decision_agent": ["决策", "选择", "哪个更好", "建议"],
            "chat_agent": ["聊天", "对话", "闲聊", "你好", "天气"],
            "executor_agent": ["执行", "运行", "启动", "部署"],
            "collaboration_agent": ["协作", "一起", "多个任务"],
        }
        
        best_match = "chat_agent"
        best_score = 0
        
        for agent, keywords in routing_rules.items():
            score = sum(1 for kw in keywords if kw in user_lower)
            if score > best_score:
                best_score = score
                best_match = agent
        
        return best_match

    def auto_dispatch(self, user_input: str) -> dict:
        """自动路由并执行"""
        target = self.vector_route(user_input)
        return self.dispatch(user_input, target)

    def dispatch(self, task: str, target_agent: str, params: dict = None) -> dict:
        """分发任务到指定 Agent"""
        try:
            module_path = f"core.agents.builtin.{target_agent}"
            module = __import__(module_path, fromlist=[target_agent])
            
            # 获取类名
            base_name = target_agent.replace('_agent', '')
            class_name = base_name[0].upper() + base_name[1:] + "Agent"
            agent_class = getattr(module, class_name)
            agent = agent_class(self.user_id)
            
            if params and 'action' in params:
                method = getattr(agent, params['action'], None)
                if method:
                    result = method(**{k: v for k, v in params.items() if k != 'action'})
                else:
                    result = agent.process(task)
            else:
                result = agent.process(task)
            
            return {"success": True, "task": task, "target": target_agent, "result": result}
        except Exception as e:
            return {"success": False, "task": task, "target": target_agent, "error": str(e)}


# 注意：不创建全局实例
