#!/usr/bin/env python3
"""Orchestrator v4.2 - 精简稳定版（任务编排）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, List, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent
from core.lib.dialect.dialect_helper import get_dialect_helper


class OrchestratorV4(BusinessAgent):
    """任务编排器 - 精简稳定版"""

    name = "orchestrator"
    description = "智慧任务编排器"
    version = "4.2.0"

    # Agent 映射
    SPECIALIST_AGENTS = {
        "code": "code_agent",
        "analysis": "analysis_agent",
        "chat": "chat_agent",
        "translate": "translate_agent",
        "calculator": "calculator_agent",
        "writer": "writer_agent",
        "director": "director_agent",
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._session_id = None
        self._agent_cache = {}
        print(f"🎯 Orchestrator v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
        return super().process(user_input, context)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[Orchestrator] 编排: {user_input[:50]}...")
        
        task_type = self._identify_task_type(user_input)
        
        if task_type in self.SPECIALIST_AGENTS:
            agent_name = self.SPECIALIST_AGENTS[task_type]
            print(f"[Orchestrator] → {agent_name}")
            result = self._delegate_to_agent(agent_name, user_input)
            return self._format_response(result, agent_name)
        
        if task_type == "complex":
            subtasks = self._decompose_task(user_input)
            results = self._execute_subtasks(subtasks)
            merged = self._merge_results(results)
            return self._format_response(merged, "orchestrator")
        
        # 降级
        result = self._delegate_to_agent("chat_agent", user_input)
        return self._format_response(result, "chat_agent")

    # ================================================================
    #  任务识别
    # ================================================================

    def _identify_task_type(self, user_input: str) -> str:
        t = user_input.lower()
        
        # 导演类
        if any(kw in t for kw in ["导演", "电影", "剧本", "拍摄", "剪辑", "后期"]):
            return "director"
        
        # 代码类
        if any(kw in t for kw in ["代码", "编程", "写一个", "函数", "算法", "debug", "修复"]):
            return "code"
        
        # 写作类
        if any(kw in t for kw in ["写", "撰写", "创作", "文章", "小说"]):
            return "writer"
        
        # 分析类
        if any(kw in t for kw in ["分析", "统计", "趋势", "数据", "报告"]):
            return "analysis"
        
        # 翻译类
        if any(kw in t for kw in ["翻译", "translate"]):
            return "translate"
        
        # 计算类
        if any(kw in t for kw in ["计算", "等于", "加", "减", "乘", "除"]):
            return "calculator"
        
        # 复杂任务
        complex_keywords = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        action_words = ["分析", "生成", "发送", "创建", "写", "计算", "翻译"]
        if any(kw in t for kw in complex_keywords) or sum(1 for aw in action_words if aw in t) >= 2:
            return "complex"
        
        # 默认聊天
        return "chat"

    # ================================================================
    #  任务分解
    # ================================================================

    def _decompose_task(self, task: str) -> List[Dict]:
        parts = re.split(r'然后|接着|之后|再', task)
        subtasks = []
        for i, part in enumerate(parts, 1):
            part = part.strip()
            if not part:
                continue
            task_type = self._identify_task_type(part)
            agent_name = self.SPECIALIST_AGENTS.get(task_type, "chat_agent")
            subtasks.append({
                "id": i,
                "description": part,
                "agent": agent_name,
                "depends_on": [i-1] if i > 1 else []
            })
        return subtasks

    # ================================================================
    #  执行
    # ================================================================

    def _delegate_to_agent(self, agent_name: str, user_input: str) -> Dict:
        agent = self._get_agent(agent_name)
        if not agent:
            return {"success": False, "response": f"Agent {agent_name} 不可用"}
        
        try:
            if hasattr(agent, 'process'):
                return agent.process(user_input, {"session_id": self._session_id})
            elif hasattr(agent, 'handle'):
                return agent.handle(user_input)
        except Exception as e:
            return {"success": False, "response": f"执行失败: {e}"}
        
        return {"success": False, "response": f"Agent {agent_name} 无可用方法"}

    def _execute_subtasks(self, subtasks: List[Dict]) -> List[Dict]:
        results = []
        for subtask in subtasks:
            result = self._delegate_to_agent(subtask["agent"], subtask["description"])
            results.append({
                "id": subtask["id"],
                "agent": subtask["agent"],
                "success": result.get("success", False),
                "output": result.get("response", result.get("output_content", ""))
            })
        return results

    def _merge_results(self, results: List[Dict]) -> Dict:
        if not results:
            return {"success": False, "response": "无结果"}
        if len(results) == 1:
            return results[0]
        
        outputs = [f"📌 {r['agent']}: {r['output'][:200]}" for r in results if r.get("output")]
        return {
            "success": all(r.get("success") for r in results),
            "response": "\n\n".join(outputs),
            "output_content": "\n\n".join(outputs),
            "subtask_results": results
        }

    # ================================================================
    #  响应格式化
    # ================================================================

    def _format_response(self, result: Dict, agent_name: str) -> Dict:
        return {
            "success": result.get("success", True),
            "response": result.get("response", result.get("output_content", "任务完成")),
            "output_content": result.get("output_content", result.get("response", "")),
            "agent": self.name,
            "executed_by": agent_name,
        }

    # ================================================================
    #  Agent 管理
    # ================================================================

    def _get_agent(self, agent_name: str):
        cache_key = f"{agent_name}:{self.user_id}"
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]
        
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
            if agent:
                self._agent_cache[cache_key] = agent
                return agent
        except Exception as e:
            print(f"[Orchestrator] 加载失败: {e}")
        
        return None

    # ================================================================
    #  统计
    # ================================================================

    def get_stats(self) -> Dict:
        return {
            "agent": self.name,
            "version": self.version,
            "cached_agents": len(self._agent_cache),
        }

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = OrchestratorV4("test")
    print("\n✅ OrchestratorV4 测试通过")
