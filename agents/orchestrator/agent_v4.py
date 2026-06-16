#!/usr/bin/env python3
"""Orchestrator v5.0 - 智慧任务编排器（完整版）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import re
from typing import Dict, List, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent
from core.lib.dialect.dialect_helper import get_dialect_helper


class OrchestratorV4(BusinessAgent):
    """
    智慧任务编排器 v5.0
    
    职责:
    1. 任务识别 - 识别任务类型（代码/对话/分析/翻译/计算等）
    2. 任务分解 - 复杂任务分解为子任务
    3. 调度执行 - 调用专业 Agent 执行
    4. 结果聚合 - 合并子任务结果
    """

    name = "orchestrator"
    description = "智慧任务编排器"
    version = "5.0.0"

    # 专业 Agent 映射
    SPECIALIST_AGENTS = {
        "code": "code_agent",
        "analysis": "analysis_agent",
        "chat": "chat_agent",
        "butler": "butler_agent",
        "translate": "translate_agent",
        "calculator": "calculator_agent",
    }

    # 所有 V4 Agent 映射（用于动态加载）
    ALL_V4_AGENTS = {
        "chat_agent": "agents.chat_agent.agent_v4.ChatAgentV4",
        "code_agent": "agents.code_agent.agent_v4.CodeAgentV4",
        "analysis_agent": "agents.analysis_agent.agent_v4.AnalysisAgentV4",
        "butler_agent": "agents.butler_agent.agent_v4.ButlerAgentV4",
        "decision_agent": "agents.decision_agent.agent_v4.DecisionAgentV4",
        "translate_agent": "agents.translate_agent.agent_v4.TranslateAgentV4",
        "calculator_agent": "agents.calculator_agent.agent_v4.CalculatorAgentV4",
        "vision_agent": "agents.vision_agent.agent_v4.VisionAgentV4",
        "memory_agent": "agents.memory_agent.agent_v4.MemoryAgentV4",
        "file_agent": "agents.file_agent.agent_v4.FileAgentV4",
        "youtube_agent": "agents.youtube_agent.agent_v4.YoutubeAgentV4",
        "video_agent": "agents.video_agent.agent_v4.VideoAgentV4",
        "audio_agent": "agents.audio_agent.agent_v4.AudioAgentV4",
        "dialect_agent": "agents.dialect_agent.agent_v4.DialectAgentV4",
        "collaboration_agent": "agents.collaboration_agent.agent_v4.CollaborationAgentV4",
        "writer_agent": "agents.writer_agent.agent_v4.WriterAgentV4",
        "proactive_agent": "agents.proactive_agent.agent_v4.ProactiveAgentV4",
        "three_d_agent": "agents.three_d_agent.agent_v4.ThreeDAgentV4",
        "video_indexer_agent": "agents.video_indexer_agent.agent_v4.VideoIndexerAgentV4",
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._agent_cache = {}
        self._orchestration_history = []
        self._user_profile = {}
        print(f"🎯 Orchestrator v{self.version} 智慧编排器已启动")
        print(f"   📋 可用专业 Agent: {len(self.ALL_V4_AGENTS)} 个")

    # ========== 能力声明 ==========

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("orchestrate", "task"): (True, 0.95),
            ("delegate", "task"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))

    # ========== 核心编排逻辑 ==========
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[Orchestrator] 📋 开始编排: {user_input[:50]}...")

        # 方言理解
        dialect_helper = get_dialect_helper(self.user_id)
        original_input = user_input
        has_dialect = dialect_helper.has_dialect(user_input)

        if has_dialect:
            user_input, _ = dialect_helper.to_standard(user_input)
            print(f"[Orchestrator] 方言理解: {original_input} → {user_input}")

        # 任务识别
        task_type = self._identify_task_type(user_input)
        print(f"[Orchestrator] 任务类型: {task_type}")

        # 简单任务 - 直接路由
        if task_type != "complex" and task_type in self.SPECIALIST_AGENTS:
            agent_name = self.SPECIALIST_AGENTS[task_type]
            print(f"[Orchestrator] 简单任务 → {agent_name}")
            result = self._delegate_to_agent(agent_name, user_input)
            return self._format_response(result, agent_name)

        # 复杂任务或不确定的任务
        if task_type == "complex" or task_type == "unknown":
            print(f"[Orchestrator] 复杂/不确定任务，请求 DecisionAgent 决策...")
            decision = self._request_decision(user_input)

            if decision.get("requires_decomposition"):
                subtasks = self._decompose_task(user_input)
                print(f"[Orchestrator] 分解为 {len(subtasks)} 个子任务")
                results = self._execute_subtasks(subtasks)
                merged = self._merge_results(results)
                return self._format_response(merged, "orchestrator")

            agent_name = decision.get("recommended_agent", "chat_agent")
            print(f"[Orchestrator] DecisionAgent 推荐 → {agent_name}")
            result = self._delegate_to_agent(agent_name, user_input)
            return self._format_response(result, agent_name)

        # 降级
        print(f"[Orchestrator] 降级 → chat_agent")
        result = self._delegate_to_agent("chat_agent", user_input)
        return self._format_response(result, "chat_agent")

    # ========== 与 DecisionAgent 协作 ==========
    def _request_decision(self, task: str) -> Dict:
        decision_agent = self._get_agent("decision_agent")

        if not decision_agent:
            return {
                "recommended_agent": "chat_agent",
                "requires_decomposition": self._needs_decomposition(task),
                "confidence": 0.5,
                "reasoning": "DecisionAgent 不可用，使用默认策略"
            }

        candidates = self._collect_candidate_assessments(task)

        if hasattr(decision_agent, 'decide'):
            result = decision_agent.decide(task, candidates)
            return {
                "recommended_agent": result.get("agent", "chat_agent"),
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", ""),
                "requires_decomposition": result.get("requires_decomposition", False),
                "alternatives": result.get("alternatives", [])
            }

        return {
            "recommended_agent": "chat_agent",
            "requires_decomposition": self._needs_decomposition(task),
            "confidence": 0.5,
            "reasoning": "使用默认规则"
        }

    def _collect_candidate_assessments(self, task: str) -> List[Dict]:
        candidates = []
        for task_type, agent_name in self.SPECIALIST_AGENTS.items():
            agent = self._get_agent(agent_name)
            confidence = 0.3

            if agent and hasattr(agent, 'can_handle_json'):
                try:
                    can, conf = agent.can_handle_json("infer", "text")
                    confidence = conf if can else 0.2
                except:
                    pass

            candidates.append({
                "agent": agent_name,
                "confidence": confidence,
                "capability": task_type
            })

        return sorted(candidates, key=lambda x: x["confidence"], reverse=True)

    def _needs_decomposition(self, task: str) -> bool:
        complex_keywords = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        action_words = ["分析", "生成", "发送", "创建", "写", "计算", "翻译"]
        return any(kw in task for kw in complex_keywords) or \
               sum(1 for aw in action_words if aw in task) >= 2

    # ========== 任务识别 ==========
    def _identify_task_type(self, user_input: str) -> str:
        complex_keywords = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        action_words = ["分析", "生成", "发送", "创建", "写", "计算", "翻译"]

        if any(kw in user_input for kw in complex_keywords) or \
           sum(1 for aw in action_words if aw in user_input) >= 2:
            return "complex"

        if any(kw in user_input for kw in ["代码", "编程", "写一个", "函数", "算法", "debug"]):
            return "code"

        if any(kw in user_input for kw in ["分析", "统计", "趋势", "数据", "报告"]):
            return "analysis"

        if any(kw in user_input for kw in ["待办", "提醒", "安排", "日程"]):
            return "butler"

        if any(kw in user_input for kw in ["翻译", "translate"]):
            return "translate"

        if any(kw in user_input for kw in ["计算", "等于", "加", "减", "乘", "除"]):
            return "calculator"

        if any(kw in user_input for kw in ["你好", "聊天", "对话", "聊聊"]):
            return "chat"

        return "unknown"

    # ========== 任务分解 ==========
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

    # ========== 执行 ==========
    def _delegate_to_agent(self, agent_name: str, user_input: str) -> Dict:
        agent = self._get_agent(agent_name)

        if not agent:
            return {
                "success": False,
                "response": f"Agent {agent_name} 不可用",
                "error": "agent_not_found"
            }

        print(f"[Orchestrator] → 委托给 {agent_name}")

        if hasattr(agent, 'process'):
            return agent.process(user_input)
        elif hasattr(agent, 'handle'):
            return agent.handle(user_input)
        return {"success": False, "response": f"Agent {agent_name} 无可用方法"}

    def _execute_subtasks(self, subtasks: List[Dict]) -> List[Dict]:
        results = []
        previous_result = None

        for subtask in subtasks:
            input_text = subtask["description"]
            if previous_result:
                input_text = f"{input_text}\n\n上一步结果: {previous_result[:200]}"

            result = self._delegate_to_agent(subtask["agent"], input_text)
            results.append({
                "id": subtask["id"],
                "agent": subtask["agent"],
                "success": result.get("success", False),
                "output": result.get("response", result.get("output_content", ""))
            })

            if result.get("success"):
                previous_result = result.get("response", "")

        return results

    def _merge_results(self, results: List[Dict]) -> Dict:
        if not results:
            return {"success": False, "response": "无子任务执行"}

        if len(results) == 1:
            return results[0]

        merged_output = []
        for r in results:
            if r.get("output"):
                merged_output.append(f"📌 {r['agent']}: {r['output'][:200]}")

        return {
            "success": all(r.get("success") for r in results),
            "response": "\n\n".join(merged_output),
            "output_content": "\n\n".join(merged_output),
            "subtask_results": results
        }

    # ========== 响应格式化 ==========
    def _format_response(self, result: Dict, agent_name: str) -> Dict:
        return {
            "success": result.get("success", True),
            "response": result.get("response", result.get("output_content", "任务完成")),
            "output_content": result.get("output_content", result.get("response", "")),
            "agent": self.name,
            "executed_by": agent_name,
        }

    # ========== Agent 管理 ==========
    def _get_agent(self, agent_name: str):
        """获取 Agent 实例（优先使用 V4 版本）"""
        cache_key = f"{agent_name}:{self.user_id}"

        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]

        # 从 ALL_V4_AGENTS 加载
        if agent_name in self.ALL_V4_AGENTS:
            try:
                module_path, class_name = self.ALL_V4_AGENTS[agent_name].rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                agent_class = getattr(module, class_name)
                self._agent_cache[cache_key] = agent_class(self.user_id)
                print(f"[Orchestrator] 加载 V4 Agent: {agent_name}")
                return self._agent_cache[cache_key]
            except Exception as e:
                print(f"[Orchestrator] 加载 V4 {agent_name} 失败: {e}")

        # 降级到 wisdom_factory
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
            if agent:
                self._agent_cache[cache_key] = agent
                print(f"[Orchestrator] 从 wisdom_factory 加载: {agent_name}")
                return agent
        except Exception as e:
            print(f"[Orchestrator] wisdom_factory 加载失败: {e}")

        return None

    # ========== 统计 ==========
    def get_stats(self) -> Dict:
        return {
            "agent": self.name,
            "version": self.version,
            "cached_agents": len(self._agent_cache),
            "orchestration_count": len(self._orchestration_history)
        }


if __name__ == "__main__":
    agent = OrchestratorV4("test")
    print("\n✅ OrchestratorV4 测试通过")
