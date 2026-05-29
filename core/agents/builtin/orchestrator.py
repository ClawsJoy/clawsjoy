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
        """关键词路由（降级方案）"""
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

    def vector_route(self, user_input: str) -> str:
        """基于向量的智能路由 + 关键词保底"""
        user_lower = user_input.lower()
        
        # 从配置文件加载关键词
        import yaml
        from pathlib import Path
        
        hard_rules = {}
        config_path = Path("config/routing_keywords.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    hard_rules = config.get('routing_keywords', {})
            except Exception as e:
                print(f"加载关键词配置失败: {e}")
        
        for agent, keywords in hard_rules.items():
            for kw in keywords:
                if kw in user_lower:
                    print(f"[关键词路由] '{user_input[:30]}...' → {agent} (匹配: {kw})")
                    return agent
        
        # 向量路由
        try:
            from core.lib.vector_knowledge_center import vector_knowledge_center
            
            collection = vector_knowledge_center._get_collection("agent_capabilities")
            if collection is None:
                return self.smart_route(user_input)
            
            results = collection.query(query_texts=[user_input], n_results=5)
            
            exclude_agents = [self.name, 'chat_agent']
            
            if results and results.get('ids') and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    agent_name = metadata.get('agent_name')
                    if agent_name and agent_name not in exclude_agents:
                        print(f"[向量路由] '{user_input[:30]}...' → {agent_name} (相似度: {results['distances'][0][i]:.2f})")
                        return agent_name
        except Exception as e:
            print(f"[向量路由] 失败: {e}")
        
        return self.smart_route(user_input)
    def auto_dispatch(self, user_input: str) -> dict:
        """自动路由并执行"""
        target = self.vector_route(user_input)
        return self.dispatch(user_input, target)

    def dispatch(self, task: str, target_agent: str, params: dict = None) -> dict:
        """分发任务到指定 Agent"""
        try:
            module_path = f"core.agents.builtin.{target_agent}"
            module = __import__(module_path, fromlist=[target_agent])
            
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
