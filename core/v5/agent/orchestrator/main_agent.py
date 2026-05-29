"""主智能体 - 完整版"""

from core.v5.agent.base import BaseAgent
from core.v5.llm.client import llm
from core.v5.memory.manager import MemoryManager
from core.v5.knowledge.graph import KnowledgeGraph
from core.v5.monitor.logger import metrics, Timing
from core.v5.utils.cache import response_cache
from typing import Dict
import time


class MainAgent(BaseAgent):
    """主智能体 - 协调所有子系统"""
    
    def __init__(self, user_id: str = "default"):
        super().__init__("main_agent", user_id)
        self.mem_mgr = MemoryManager(user_id, "main_agent")
        self.knowledge = KnowledgeGraph(user_id)
        self._init_knowledge()
        print("🧠 主智能体已启动 (完整版)")
    
    def _init_knowledge(self):
        """初始化知识图谱"""
        if self.knowledge.nodes:
            return
        
        concepts = [
            ("python", "Python", "concept", {"用途": "数据分析、AI、Web开发"}),
            ("java", "Java", "concept", {"用途": "企业级应用、Android开发"}),
            ("ai", "人工智能", "concept", {"包含": "机器学习、深度学习、自然语言处理"}),
            ("ml", "机器学习", "concept", {"包含": "监督学习、无监督学习、强化学习"})
        ]
        for cid, name, ctype, props in concepts:
            self.knowledge.add_node(cid, name, ctype, props)
        
        relations = [
            ("python", "ai", "用于", 0.9),
            ("python", "ml", "用于", 0.8),
            ("java", "android", "用于", 0.9)
        ]
        for f, t, r, w in relations:
            self.knowledge.add_relation(f, t, r, w)
    
    @Timing(metrics, "agent_process")
    def process(self, user_input: str) -> Dict:
        """处理用户输入"""
        # 检查缓存
        cached = response_cache.get(self.user_id, user_input)
        if cached:
            metrics.record("cache_hit", 1)
            self.record_history(user_input, cached)
            return {
                "success": True,
                "intent": "cached",
                "response": cached,
                "user_id": self.user_id
            }
        
        self.update_stats()
        
        intent = self._analyze_intent(user_input)
        
        start_time = time.time()
        
        if intent == "plan":
            response = self._make_plan(user_input)
        elif intent == "decision":
            response = self._make_decision(user_input)
        elif intent == "query_knowledge":
            response = self._query_knowledge(user_input)
        else:
            response = self._chat(user_input)
        
        elapsed = time.time() - start_time
        metrics.record("response_time", elapsed)
        
        # 记录历史
        self.record_history(user_input, response)
        self.mem_mgr.add_history(user_input, response)
        
        # 存入缓存
        response_cache.set(self.user_id, user_input, response)
        
        return {
            "success": True,
            "intent": intent,
            "response": response,
            "user_id": self.user_id
        }
    
    def _analyze_intent(self, text: str) -> str:
        if any(k in text for k in ["计划", "规划", "步骤", "怎么做", "如何"]):
            return "plan"
        if any(k in text for k in ["决策", "建议", "选择", "哪个好", "推荐"]):
            return "decision"
        if any(k in text for k in ["什么是", "解释", "知识", "关系", "介绍"]):
            return "query_knowledge"
        return "chat"
    
    def _make_plan(self, goal: str) -> str:
        prompt = f"""将以下目标分解为具体可执行的步骤，每步要具体、可操作:
{goal}

请按格式输出:
1. 第一步: xxx
2. 第二步: xxx
..."""
        return llm.generate(prompt)
    
    def _make_decision(self, question: str) -> str:
        prompt = f"""请分析以下问题，给出决策建议:
{question}

请按格式输出:
问题分析: 
可选方案: 
推荐方案: 
理由: 
风险等级: 高/中/低"""
        return llm.generate(prompt)
    
    def _query_knowledge(self, query: str) -> str:
        query_lower = query.lower()
        for node_id in self.knowledge.nodes:
            if node_id in query_lower:
                related = self.knowledge.query_related(node_id)
                if related:
                    result = f"📚 关于 {node_id.upper()} 的相关知识:\n"
                    for r in related[:5]:
                        result += f"- {r['name']}: {r.get('relation', '相关')}\n"
                    return result
        
        prompt = f"请用简单易懂的语言解释:\n{query}\n\n解释:"
        return llm.generate(prompt)
    
    def _chat(self, message: str) -> str:
        prompt = f"用户: {message}\n助手:"
        return llm.generate(prompt)
    
    def get_state(self) -> Dict:
        return {
            "name": self.name,
            "user_id": self.user_id,
            "stats": self.memory.get('stats', {}),
            "preferences": self.memory.get('preferences', {}),
            "knowledge": self.knowledge.get_stats(),
            "memory": self.mem_mgr.get_stats(),
            "metrics": metrics.get_stats(),
            "cache": response_cache.get_stats()
        }
