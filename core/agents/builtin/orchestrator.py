# version: 2.0.0 - 四引擎完整版 (LLM+向量+配置+规则)
# 更新日期: 2026-06-02

"""Orchestrator - 四引擎完整版（兼容 OrchestratorAgent）"""

from typing import Dict, List, Optional
from core.lib.unified_config import unified_config


class OrchestratorV6:
    """智能体编排器 V6 - 四引擎完整版"""
    
    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id
        self._intent_map = None
        self._route_stats = {"total": 0, "keyword_hits": 0, "vector_hits": 0, "fallback": 0, "avg_time_ms": 0}
    
    # ========== 四引擎调用链 ==========
    
    def _llm_understand(self, message: str):
        try:
            from engine.semantic.engines.llm_engine import llm_engine
            if llm_engine.is_available():
                intent, conf, _ = llm_engine.understand(message)
                if conf > 0.3:
                    return intent, conf, "llm"
        except:
            pass
        return None, 0, None
    
    def _vector_understand(self, message: str):
        try:
            from core.lib.vector_knowledge_center import vector_knowledge_center
            skills_collection = vector_knowledge_center.collections.get("skills")
            if skills_collection:
                results = skills_collection.query(query_texts=[message], n_results=3)
                if results and results.get('metadatas') and results['metadatas'][0]:
                    meta = results['metadatas'][0][0]
                    intent = meta.get('name', 'unknown')
                    dist = results['distances'][0][0] if results.get('distances') else 1
                    conf = 1 - min(dist, 1.0)
                    if conf > 0.3:
                        return intent, conf, "vector"
        except:
            pass
        return None, 0, None
    
    def _config_understand(self, message: str):
        try:
            from engine.semantic.engines.config_engine import config_engine
            intent, conf, _ = config_engine.understand(message)
            if conf > 0.2:
                return intent, conf, "config"
        except:
            pass
        return None, 0, None
    
    def _rule_understand(self, message: str):
        try:
            from engine.semantic.engines.rule_engine import rule_engine
            intent, conf, _ = rule_engine.understand(message)
            return intent, conf, "rule"
        except:
            return "unknown", 0, "rule"
    
    # ========== Agent 映射 ==========
    
    def _get_intent_map(self) -> Dict:
        if self._intent_map is not None:
            return self._intent_map
        capabilities = unified_config.get("keywords.agent_capabilities", {})
        intent_map = {}
        for agent_name in capabilities.keys():
            base_name = agent_name.replace('_agent', '').replace('_skill', '')
            intent_map[base_name] = agent_name
            intent_map[agent_name] = agent_name
        extra_map = {
            'weather': 'weather_skill', 'translate': 'translate_agent',
            'code': 'code_agent', 'video': 'video_agent',
            'analysis': 'analysis_agent', 'memory': 'memory_agent',
            'greeting': 'chat_agent', 'thanks': 'chat_agent',
            'farewell': 'chat_agent', 'calculate': 'calculator',
        }
        intent_map.update(extra_map)
        self._intent_map = intent_map
        return intent_map
    
    def _intent_to_agent(self, intent: str) -> str:
        intent_map = self._get_intent_map()
        if intent in intent_map:
            return intent_map[intent]
        if intent + "_agent" in intent_map:
            return intent + "_agent"
        return "chat_agent"
    
    # ========== 核心路由 ==========
    
    def smart_route(self, message: str) -> str:
        intent, conf, source = self._llm_understand(message)
        if intent:
            print(f"[Orchestrator] LLM: {intent}({conf:.2f})")
            return self._intent_to_agent(intent)
        intent, conf, source = self._vector_understand(message)
        if intent:
            print(f"[Orchestrator] 向量: {intent}({conf:.2f})")
            return self._intent_to_agent(intent)
        intent, conf, source = self._config_understand(message)
        if intent:
            print(f"[Orchestrator] 配置: {intent}({conf:.2f})")
            return self._intent_to_agent(intent)
        intent, conf, source = self._rule_understand(message)
        print(f"[Orchestrator] 规则: {intent}({conf:.2f})")
        return self._intent_to_agent(intent)
    
    def decompose_task(self, task: str) -> Dict:
        try:
            from engine.semantic import semantic_engine
            result = semantic_engine.understand(task)
            return {'intent': result.intent, 'subtasks': []}
        except:
            return {'intent': 'unknown', 'subtasks': []}
    
    # ========== 兼容方法 ==========
    
    def agent_decide_route(self, user_input: str, candidates: list) -> str:
        for agent_name in candidates:
            try:
                module = __import__(f"core.agents.builtin.{agent_name}", fromlist=[agent_name])
                class_name = agent_name.replace('_', ' ').title().replace(' ', '') + "Agent"
                agent_class = getattr(module, class_name)
                agent = agent_class(self.user_id)
                if hasattr(agent, 'can_handle'):
                    result = agent.can_handle(user_input)
                    if result.get('can', False):
                        return agent_name
            except:
                continue
        return candidates[0] if candidates else "chat_agent"
    
    def vector_route(self, user_input: str) -> str:
        intent, conf, _ = self._vector_understand(user_input)
        if intent:
            return self._intent_to_agent(intent)
        return "chat_agent"
    
    def auto_dispatch(self, user_input: str) -> dict:
        target = self.smart_route(user_input)
        return {"target": target, "confidence": 0.8}
    
    def dispatch(self, task: str, target_agent: str, params: dict = None) -> dict:
        try:
            module = __import__(f"core.agents.builtin.{target_agent}", fromlist=[target_agent])
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
    
    def _record_route(self, route_type: str, duration_ms: float):
        self._route_stats["total"] += 1
        if route_type == "keyword":
            self._route_stats["keyword_hits"] += 1
        elif route_type == "vector":
            self._route_stats["vector_hits"] += 1
        else:
            self._route_stats["fallback"] += 1
        total = self._route_stats["total"]
        old_avg = self._route_stats["avg_time_ms"]
        self._route_stats["avg_time_ms"] = old_avg + (duration_ms - old_avg) / total if total > 0 else duration_ms
    
    def get_route_stats(self) -> dict:
        return self._route_stats


# 兼容别名
class OrchestratorAgent(OrchestratorV6):
    pass


orchestrator = OrchestratorV6()
