#!/usr/bin/env python3
"""Orchestrator - Orchestrator 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

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
        self._load_agent_config()
        super().__init__(user_id=user_id)
        self.behavior = workspace_manager.get_behavior_config("orchestrator")
        print(f"[Orchestrator] 初始化完成")

    def smart_route(self, user_input: str) -> str:
        """关键词路由 - 从 routing_keywords.yaml 读取"""
        user_lower = user_input.lower()
        
        # 加载路由配置
        try:
            with open('config/routing_keywords.yaml', 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                routing_keywords = config.get('routing_keywords', {})
        except:
            routing_keywords = {}
        
        best_match = "chat_agent"
        best_score = 0
        
        for agent, keywords in routing_keywords.items():
            score = sum(1 for kw in keywords if kw in user_lower)
            if score > best_score:
                best_score = score
                best_match = agent
        
        return best_match


    def agent_decide_route(self, user_input: str, candidates: list) -> str:
        """让候选 Agent 自己决定是否适合处理"""
        for agent_name in candidates:
            try:
                module = __import__(f"core.agents.builtin.{agent_name}", fromlist=[agent_name])
                class_name = agent_name.replace('_', ' ').title().replace(' ', '') + "Agent"
                agent_class = getattr(module, class_name)
                agent = agent_class(self.user_id)
                
                # 询问 Agent 是否适合
                if hasattr(agent, 'can_handle'):
                    result = agent.can_handle(user_input)
                    if result.get('can', False):
                        print(f"[Agent自决] '{user_input[:30]}...' → {agent_name} (置信度: {result.get('confidence', 0)})")
                        return agent_name
            except Exception as e:
                continue
        return candidates[0] if candidates else "chat_agent"

    def vector_route(self, user_input: str) -> str:
        """基于向量的智能路由（向量优先，关键词降级）"""
        user_lower = user_input.lower()
        
        # 1. 向量检索（优先）
        try:
            from core.lib.vector_knowledge_center import vector_knowledge_center
            
            collection = vector_knowledge_center._get_collection("agent_capabilities")
            if collection:
                results = collection.query(query_texts=[user_input], n_results=3)
                
                exclude_agents = [self.name]
                
                if results and results.get('ids') and results['ids'][0]:
                    for i, doc_id in enumerate(results['ids'][0]):
                        metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                        agent_name = metadata.get('agent_name')
                        score = results['distances'][0][i] if results.get('distances') else 1.0
                        
                        if agent_name and agent_name not in exclude_agents:
                            # 相似度阈值 0.7（越低越相似）
                            if score < 1.3:
                                print(f"[向量路由] '{user_input[:30]}...' → {agent_name} (相似度: {score:.2f})")
                                self._record_route("vector", 0)
                                return agent_name
                            else:
                                print(f"[向量路由] 相似度不足: {agent_name} (score={score:.2f})")
        except Exception as e:
            print(f"[向量路由] 失败: {e}")
        
        # 2. 关键词路由（降级）
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
                    self._record_route("keyword", 0)
                    return agent
        
        # 3. 默认降级
        self._record_route("fallback", 0)
        return "chat_agent"
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

    # 路由统计
    _route_stats = {
        "total": 0,
        "keyword_hits": 0,
        "vector_hits": 0,
        "fallback": 0,
        "avg_time_ms": 0
    }
    
    def _record_route(self, route_type: str, duration_ms: float):
        """记录路由统计"""
        self._route_stats["total"] += 1
        if route_type == "keyword":
            self._route_stats["keyword_hits"] += 1
        elif route_type == "vector":
            self._route_stats["vector_hits"] += 1
        else:
            self._route_stats["fallback"] += 1
        
        # 更新平均耗时
        total = self._route_stats["total"]
        old_avg = self._route_stats["avg_time_ms"]
        self._route_stats["avg_time_ms"] = old_avg + (duration_ms - old_avg) / total
    
    def get_route_stats(self) -> dict:
        """获取路由统计"""
        return self._route_stats
