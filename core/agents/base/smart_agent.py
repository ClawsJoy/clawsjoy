#!/usr/bin/env python3
"""Smart Agent v2 - 真正的智能基类

核心智能特性:
1. 自我认知 - 知道自己能做什么
2. 自主学习 - 从经验中改进
3. 智能决策 - 多维度判断
4. 任务分解 - 复杂任务拆分
5. 反思优化 - 结果自评改进
"""

import json
import time
from abc import abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from core.agents.base.communicable_agent import CommunicableAgent
from core.agents.base.mixins.config_mixin import ConfigMixin
from core.agents.base.mixins.lifecycle_mixin import LifecycleMixin
from core.agents.base.mixins.memory_mixin import MemoryMixin
from core.lib.unified_config import unified_config


class SmartAgent(CommunicableAgent, LifecycleMixin, ConfigMixin, MemoryMixin):
    """
    真正的智能基类 - 具备自我认知、学习、决策能力

    核心智能特性:
    - 自我认知: 知道自己的能力边界
    - 自主学习: 从成功/失败中学习
    - 智能决策: 基于多维度评估
    - 任务分解: 复杂任务自动拆分
    - 反思优化: 结果自评并改进
    """

    name = "smart_agent"
    description = "智能体基类"
    type = "core"
    version = "3.0.0"

    def __init__(self, user_id: str = "default") -> None:
        super().__init__(user_id=user_id)

        # ========== 自我认知 ==========
        self.birth_time = datetime.now()
        self._capabilities = []  # 能力列表
        self._capability_scores = defaultdict(float)  # 能力置信度

        # ========== 学习数据 ==========
        self.experiences = []  # 经验库
        self._success_history = defaultdict(list)  # 按任务类型的成功历史
        self._performance_stats = {
            "total_tasks": 0,
            "success_count": 0,
            "avg_response_time": 0,
            "learning_iterations": 0,
        }

        # ========== 决策参数 ==========
        self.confidence_threshold = 0.6  # 自信阈值
        self.learning_rate = 0.1  # 学习率
        self.max_retries = 2  # 最大重试次数

        # ========== 加载配置 ==========
        self._load_intelligent_config()

        print(f"[{self.name}] 🧠 智能体初始化完成 v{self.version}")

        self._init_memory_dir()
        self._init_lifecycle()
        self._load_config()
        self._load_memory()

    # ==================== 自我认知 ====================

    def know_thyself(self) -> Dict:
        """自知之明 - 了解自己的能力"""
        return {
            "name": self.name,
            "capabilities": self._capabilities,
            "capability_scores": dict(self._capability_scores),
            "specialties": self._get_specialties(),
            "limitations": self._get_limitations(),
            "experience_count": len(self.experiences),
            "success_rate": self._get_success_rate(),
        }

    def can_handle(self, user_input: str) -> Dict:
        """
        智能判断是否能处理该请求
        多维度评估：能力匹配 + 历史成功率 + 语义相似度
        """
        # 1. 能力匹配度
        capability_match = self._calculate_capability_match(user_input)

        # 2. 历史成功率
        historical_success = self._get_historical_success_rate(user_input)

        # 3. 语义相似度（基于之前成功的任务）
        semantic_similarity = self._calculate_semantic_similarity(user_input)

        # 4. LLM 辅助判断（可选，较慢）
        llm_judgment = self._llm_judge_capability(user_input)

        # 综合置信度
        confidence = (
            capability_match * 0.35
            + historical_success * 0.35
            + semantic_similarity * 0.20
            + llm_judgment * 0.10
        )

        can = confidence >= self.confidence_threshold

        return {
            "can": can,
            "confidence": round(confidence, 3),
            "capability_match": round(capability_match, 3),
            "historical_success": round(historical_success, 3),
            "reason": self._get_decision_reason(can, confidence),
        }

    def _calculate_capability_match(self, user_input: str) -> float:
        """计算能力匹配度"""
        if not self._capabilities:
            return 0.5  # 未知能力，中性评分

        user_lower = user_input.lower()
        matched = 0
        for cap in self._capabilities:
            if cap.lower() in user_lower:
                matched += self._capability_scores.get(cap, 0.5)

        return min(matched / max(len(self._capabilities), 1), 1.0)

    def _get_historical_success_rate(self, user_input: str) -> float:
        """获取历史成功率"""
        # 找到最相似的任务类型
        task_type = self._classify_task_type(user_input)
        history = self._success_history.get(task_type, [])
        if not history:
            return 0.5  # 无历史，中性评分

        return sum(history) / len(history)

    def _calculate_semantic_similarity(self, user_input: str) -> float:
        """计算与之前成功任务的语义相似度"""
        if not self.experiences:
            return 0.0

        # 简化版：关键词重叠度
        words = set(user_input.lower().split())
        best_similarity = 0.0

        for exp in self.experiences[-20:]:  # 最近20个经验
            if exp.get("success", False):
                exp_words = set(exp.get("input", "").lower().split())
                if exp_words:
                    overlap = len(words & exp_words) / max(len(words), len(exp_words))
                    best_similarity = max(best_similarity, overlap)

        return best_similarity

    def _llm_judge_capability(self, user_input: str) -> float:
        """使用 LLM 辅助判断（可选，较慢）"""
        try:
            from engine.semantic import semantic_engine

            result = semantic_engine.understand(user_input)
            # 如果语义引擎返回的意图与自己的能力相关，提高置信度
            if result.intent in self._capabilities:
                return result.confidence
            return 0.3
        except Exception as e:
            return 0.3  # LLM 不可用时，保守评分

    # ==================== 智能决策 ====================

    def should_delegate(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """是否应该委托给其他 Agent"""
        my_capability = self.can_handle(user_input)

        if my_capability["can"] and my_capability["confidence"] > 0.7:
            return False, None

        # 查询其他 Agent 的能力
        best_agent = None
        best_confidence = 0

        for agent_name in self._get_available_agents():
            if agent_name == self.name:
                continue
            # 委托给 Orchestrator 决策
            pass

        return best_confidence > my_capability["confidence"], best_agent

    def decompose_task(self, task: str) -> List[Dict]:
        """任务分解 - 将复杂任务拆分为子任务"""
        subtasks = []

        # 1. 识别任务类型
        task_type = self._classify_task_type(task)

        # 2. 根据类型分解
        if task_type == "coding":
            subtasks = self._decompose_coding_task(task)
        elif task_type == "analysis":
            subtasks = self._decompose_analysis_task(task)
        elif task_type == "writing":
            subtasks = self._decompose_writing_task(task)
        else:
            subtasks = [{"type": "direct", "action": task, "deps": []}]

        # 3. 记录分解结果
        self.record_experience(
            {
                "type": "decomposition",
                "input": task,
                "subtasks": len(subtasks),
                "success": len(subtasks) > 0,
            }
        )

        return subtasks

    def _decompose_coding_task(self, task: str) -> List[Dict]:
        """分解编程任务"""
        return [
            {"type": "analyze", "action": "分析需求", "deps": []},
            {"type": "design", "action": "设计方案", "deps": ["analyze"]},
            {"type": "implement", "action": "编写代码", "deps": ["design"]},
            {"type": "test", "action": "测试验证", "deps": ["implement"]},
        ]

    def _decompose_analysis_task(self, task: str) -> List[Dict]:
        """分解分析任务"""
        return [
            {"type": "collect", "action": "收集数据", "deps": []},
            {"type": "process", "action": "处理数据", "deps": ["collect"]},
            {"type": "analyze", "action": "分析结果", "deps": ["process"]},
            {"type": "report", "action": "生成报告", "deps": ["analyze"]},
        ]

    def _decompose_writing_task(self, task: str) -> List[Dict]:
        """分解写作任务"""
        return [
            {"type": "outline", "action": "制定大纲", "deps": []},
            {"type": "draft", "action": "撰写草稿", "deps": ["outline"]},
            {"type": "revise", "action": "修改润色", "deps": ["draft"]},
            {"type": "finalize", "action": "最终定稿", "deps": ["revise"]},
        ]

    # ==================== 学习与反思 ====================

    def learn_from_experience(self, experience: Dict) -> None:
        """从经验中学习"""
        self.experiences.append(experience)

        # 更新成功/失败统计
        task_type = experience.get("task_type", "unknown")
        success = experience.get("success", False)
        self._success_history[task_type].append(1 if success else 0)

        # 限制历史长度
        if len(self._success_history[task_type]) > 100:
            self._success_history[task_type] = self._success_history[task_type][-100:]

        # 更新能力置信度
        if "capability_used" in experience:
            cap = experience["capability_used"]
            current = self._capability_scores.get(cap, 0.5)
            adjustment = self.learning_rate * (1 if success else -0.5)
            self._capability_scores[cap] = max(0, min(1, current + adjustment))

        # 更新统计
        self._performance_stats["learning_iterations"] += 1

    def reflect_on_result(self, result: Dict) -> Dict:
        """反思结果，生成改进建议"""
        reflection = {
            "success": result.get("success", False),
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
        }

        # 评分
        if result.get("success"):
            reflection["score"] += 60
            reflection["strengths"].append("任务完成")

        if result.get("response_time", 0) < 1000:
            reflection["score"] += 20
            reflection["strengths"].append("响应快速")
        else:
            reflection["weaknesses"].append("响应较慢")

        if result.get("accuracy", 1.0) > 0.8:
            reflection["score"] += 20
            reflection["strengths"].append("准确度高")

        # 改进建议
        if reflection["score"] < 70:
            reflection["improvements"].append("考虑使用更好的策略")

        return reflection

    def optimize_self(self) -> Dict:
        """自我优化 - 基于历史表现调整参数"""
        success_rate = self._get_success_rate()

        optimizations = {}

        # 调整置信度阈值
        if success_rate > 0.8:
            old = self.confidence_threshold
            self.confidence_threshold = min(0.8, old + 0.05)
            optimizations["confidence_threshold"] = {
                "old": old,
                "new": self.confidence_threshold,
            }
        elif success_rate < 0.5:
            old = self.confidence_threshold
            self.confidence_threshold = max(0.4, old - 0.05)
            optimizations["confidence_threshold"] = {
                "old": old,
                "new": self.confidence_threshold,
            }

        # 调整学习率
        if self._performance_stats["learning_iterations"] > 50:
            self.learning_rate = max(0.05, self.learning_rate * 0.95)
            optimizations["learning_rate"] = {"new": self.learning_rate}

        return optimizations

    # ==================== 核心方法 ====================

    @abstractmethod
    def process(self, user_input: str, context: dict = None) -> dict:
        """处理用户输入（子类实现具体逻辑）"""
        pass

    def handle(self, user_input: str, context: dict = None) -> dict:
        """智能处理入口"""
        start_time = time.time()

        # 1. 自我评估
        self_assessment = self.know_thyself()

        # 2. 决策
        decision = self.can_handle(user_input)

        if not decision["can"]:
            # 尝试委托
            should_delegate, target = self.should_delegate(user_input)
            if should_delegate and target:
                return self._delegate_to(target, user_input)

        # 3. 任务分解（如果是复杂任务）
        if self._is_complex_task(user_input):
            subtasks = self.decompose_task(user_input)
            result = self._execute_with_subtasks(subtasks)
        else:
            # 4. 直接处理
            result = self.process(user_input, context)

        # 5. 反思
        result["response_time"] = (time.time() - start_time) * 1000
        reflection = self.reflect_on_result(result)
        result["reflection"] = reflection

        # 6. 学习
        self.learn_from_experience(
            {
                "input": user_input,
                "result": result.get("response", ""),
                "success": result.get("success", False),
                "task_type": self._classify_task_type(user_input),
                "response_time": result["response_time"],
            }
        )

        return result

    # ==================== 辅助方法 ====================

    def _get_specialties(self) -> List[str]:
        """获取专长领域"""
        return [cap for cap, score in self._capability_scores.items() if score > 0.7]

    def _get_limitations(self) -> List[str]:
        """获取限制"""
        return [cap for cap, score in self._capability_scores.items() if score < 0.3]

    def _get_success_rate(self) -> float:
        """获取整体成功率"""
        if self._performance_stats["total_tasks"] == 0:
            return 0.5
        return (
            self._performance_stats["success_count"]
            / self._performance_stats["total_tasks"]
        )

    def _classify_task_type(self, user_input: str) -> str:
        """分类任务类型"""
        input_lower = user_input.lower()

        if any(kw in input_lower for kw in ["代码", "编程", "写", "函数"]):
            return "coding"
        if any(kw in input_lower for kw in ["分析", "统计", "数据", "报告"]):
            return "analysis"
        if any(kw in input_lower for kw in ["写", "文章", "文档", "说明"]):
            return "writing"
        if any(kw in input_lower for kw in ["天气", "温度", "下雨"]):
            return "weather"
        if any(kw in input_lower for kw in ["计算", "加", "减", "乘", "除"]):
            return "calculation"

        return "chat"

    def _is_complex_task(self, user_input: str) -> bool:
        """判断是否为复杂任务"""
        # 长度 > 50 或包含多个任务关键词
        if len(user_input) > 50:
            return True

        complex_indicators = ["并且", "同时", "然后", "之后", "接着"]
        return any(ind in user_input for ind in complex_indicators)

    def _execute_with_subtasks(self, subtasks: List[Dict]) -> Dict:
        """执行子任务链"""
        results = {}
        for subtask in subtasks:
            # 检查依赖
            deps_satisfied = all(dep in results for dep in subtask.get("deps", []))
            if not deps_satisfied:
                continue

            # 执行子任务
            result = self.process(subtask["action"])
            results[subtask["type"]] = result

        # 合并结果
        return {
            "success": True,
            "response": "\n".join([r.get("response", "") for r in results.values()]),
            "subtask_results": results,
        }

    def _delegate_to(self, target_agent: str, user_input: str) -> Dict:
        """委托给其他 Agent"""
        self.bus_publish(
            f"agent.{target_agent}.delegate",
            {
                "from": self.name,
                "input": user_input,
            },
        )
        return {
            "success": True,
            "response": f"我将把这个问题转交给 {target_agent} 处理。",
            "delegated_to": target_agent,
        }

    def _get_available_agents(self) -> List[str]:
        """获取可用 Agent 列表"""
        try:
            from core.lib.agent_registry import agent_registry

            return agent_registry.list_agents()
        except Exception as e:
            return ["chat_agent", "code_agent"]

    def _get_decision_reason(self, can: bool, confidence: float) -> str:
        """获取决策理由"""
        if can:
            return f"我能处理，置信度 {confidence:.0%}"
        return f"我不能处理，置信度仅 {confidence:.0%}"

    # ==================== 经验管理 ====================

    def record_experience(self, experience: Dict) -> None:
        """记录经验（兼容原接口）"""
        experience["timestamp"] = datetime.now().isoformat()
        self.experiences.append(experience)

        if len(self.experiences) > 100:
            self.experiences = self.experiences[-100:]

    def share_experience(self, target_agent: str, experience_id: int) -> bool:
        """分享经验给其他 Agent"""
        if experience_id >= len(self.experiences):
            return False
        exp = self.experiences[experience_id]
        self.bus_publish(f"agent.{target_agent}.experience", exp)
        return True

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "name": self.name,
            "version": self.version,
            "total_tasks": self._performance_stats["total_tasks"],
            "success_rate": self._get_success_rate(),
            "avg_response_time": self._performance_stats["avg_response_time"],
            "experience_count": len(self.experiences),
            "capabilities": self._capabilities,
            "specialties": self._get_specialties(),
        }

    def get_memory(self, key: str, default=None) -> Any:
        """获取记忆"""
        return self._memory.get(key, default)

    def set_memory(self, key: str, value) -> None:
        """设置记忆"""
        self._memory[key] = value

    def register_capability(self, capability: str, initial_score: float = 0.5):
        """注册能力"""
        if capability not in self._capabilities:
            self._capabilities.append(capability)
        self._capability_scores[capability] = initial_score
        print(f"[{self.name}] 已注册能力: {capability} (初始置信度: {initial_score})")

    def _load_intelligent_config(self):
        """加载智能配置"""
        # 从配置文件加载智能参数
        self.confidence_threshold = unified_config.get(
            "smart.confidence_threshold", 0.6
        )
        self.learning_rate = unified_config.get("smart.learning_rate", 0.1)
        self.max_retries = unified_config.get("smart.max_retries", 2)

    def _subscribe_events(self):
        """订阅系统事件"""
        try:
            from core.lib.agent_communication import agent_communication

            # 订阅任务事件
            agent_communication.subscribe(self.name, "task.arrived")
            agent_communication.subscribe(self.name, "reminder.trigger")
            print(f"[{self.name}] 已订阅系统事件")
        except Exception as e:
            pass

    def _on_event(self, event_type: str, payload: Dict):
        """处理事件（子类可覆盖）"""
        if event_type == "task.arrived":
            print(f"[{self.name}] 收到主动任务: {payload.get('task')}")
        elif event_type == "reminder.trigger":
            print(f"[{self.name}] 收到提醒: {payload.get('content')}")
