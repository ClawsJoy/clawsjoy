#!/usr/bin/env python3
"""Smart Agent v3.0 - LLM-First 智能基类

核心智能特性:
1. 自我认知 - 知道自己能做什么（由 LLM 判断）
2. 自主学习 - 从经验中改进
3. 智能决策 - 由 LLM 多维度评估
4. 任务分解 - 由 LLM 动态拆分
5. 反思优化 - 结果自评改进
"""

import json
import time
from abc import abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.agents.base.communicable_agent import CommunicableAgent
from core.agents.base.mixins.config_mixin import ConfigMixin
from core.agents.base.mixins.lifecycle_mixin import LifecycleMixin
from core.agents.base.mixins.memory_mixin import MemoryMixin
from core.lib.unified_config import unified_config


class SmartAgent(CommunicableAgent, LifecycleMixin, ConfigMixin, MemoryMixin):
    """
    LLM-First 智能基类
    
    核心设计：
    - 所有意图判断、任务分类、能力评估由 LLM 完成
    - 基类只保留学习、反思、经验管理（不阻碍 LLM）
    """

    name = "smart_agent"
    description = "智能体基类"
    type = "core"
    version = "3.0.0"

    def __init__(self, user_id: str = "default") -> None:
        super().__init__(user_id=user_id)

        # ========== 自我认知（由 LLM 动态评估）==========
        self.birth_time = datetime.now()
        self._capability_descriptions = []  # 能力描述（供 LLM 理解）
        self._capability_scores = defaultdict(float)  # 历史置信度

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

        print(f"[{self.name}] 🧠 LLM-First 智能体初始化完成 v{self.version}")

        self._init_memory_dir()
        self._init_lifecycle()
        self._load_config()
        self._load_memory()

    # ==================== 自我认知 ====================

    def know_thyself(self) -> Dict:
        """自知之明 - 返回能力描述供 LLM 评估"""
        return {
            "name": self.name,
            "description": self.description,
            "capability_descriptions": self._capability_descriptions,
            "capability_scores": dict(self._capability_scores),
            "specialties": self._get_specialties(),
            "limitations": self._get_limitations(),
            "experience_count": len(self.experiences),
            "success_rate": self._get_success_rate(),
        }

    def can_handle(self, user_input: str, context: Dict = None) -> Dict:
        """
        由 LLM 评估是否能处理该请求
        返回：评估结果
        """
        # 1. 构建 LLM 评估 Prompt
        prompt = self._build_can_handle_prompt(user_input, context)
        
        # 2. 调用 LLM 评估
        try:
            result = self._call_llm_for_evaluation(prompt)
            if result and "can" in result:
                return {
                    "can": result.get("can", False),
                    "confidence": result.get("confidence", 0.5),
                    "reason": result.get("reason", "LLM 评估"),
                    "capability_match": result.get("capability_match", 0.5),
                    "historical_success": result.get("historical_success", 0.5),
                }
        except Exception as e:
            print(f"[{self.name}] LLM 评估失败: {e}")
        
        # 3. 降级：基于历史成功率
        historical = self._get_historical_success_rate(user_input)
        can = historical > self.confidence_threshold
        
        return {
            "can": can,
            "confidence": historical,
            "reason": "基于历史成功率降级评估",
            "capability_match": 0.5,
            "historical_success": historical,
        }

    def _build_can_handle_prompt(self, user_input: str, context: Dict) -> str:
        """构建 LLM 能力评估 Prompt"""
        return f"""你是 {self.name}（{self.description}），请判断是否能处理以下用户请求。

## 用户请求
{user_input}

## 你的能力描述
{json.dumps(self._capability_descriptions, ensure_ascii=False, indent=2)}

## 历史成功率
{self._get_success_rate():.0%}

## 输出格式（只输出 JSON）
{{"can": true/false, "confidence": 0.0-1.0, "reason": "简短理由", "capability_match": 0.0-1.0, "historical_success": 0.0-1.0}}

只输出 JSON：
"""

    def _call_llm_for_evaluation(self, prompt: str) -> Optional[Dict]:
        """调用 LLM 进行评估"""
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 256,
                        "temperature": 0.1,
                    }
                },
                timeout=20
            )
            if resp.status_code == 200:
                response = resp.json().get("response", "")
                # 提取 JSON
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            print(f"[{self.name}] LLM 调用失败: {e}")
        return None

    # ==================== 智能决策 ====================

    def should_delegate(self, user_input: str, context: Dict = None) -> Tuple[bool, Optional[str]]:
        """
        由 LLM 评估是否需要委托给其他 Agent
        """
        # 构建评估 Prompt
        prompt = f"""你是 {self.name}，请判断是否应该将以下请求委托给其他 Agent。

## 用户请求
{user_input}

## 可用 Agent
{self._get_available_agents()}

## 你的能力
{self._capability_descriptions}

## 输出 JSON
{{"should_delegate": true/false, "target_agent": "agent_name", "reason": "理由"}}

只输出 JSON：
"""
        try:
            result = self._call_llm_for_evaluation(prompt)
            if result:
                return result.get("should_delegate", False), result.get("target_agent")
        except:
            pass
        
        return False, None

    def decompose_task(self, task: str, context: Dict = None) -> List[Dict]:
        """
        由 LLM 动态分解任务
        """
        prompt = f"""请将以下任务分解为子任务（JSON 格式）。

## 任务
{task}

## 可用动作
analyze, generate, search, calculate, translate, chat, write, review, fix

## 输出格式
[
  {{"id": 1, "action": "analyze", "target": "data", "description": "描述", "deps": []}},
  {{"id": 2, "action": "generate", "target": "code", "description": "描述", "deps": [1]}}
]

只输出 JSON 数组：
"""
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 512,
                        "temperature": 0.3,
                    }
                },
                timeout=30
            )
            if resp.status_code == 200:
                response = resp.json().get("response", "")
                import re
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    subtasks = json.loads(match.group())
                    if isinstance(subtasks, list) and len(subtasks) > 0:
                        # 记录分解结果
                        self.record_experience({
                            "type": "decomposition",
                            "input": task,
                            "subtasks": len(subtasks),
                            "success": True,
                        })
                        return subtasks
        except Exception as e:
            print(f"[{self.name}] 任务分解失败: {e}")

        # 降级：单一任务
        return [{"id": 1, "action": "process", "target": "task", "description": task, "deps": []}]

    # ==================== 学习与反思 ====================

    def learn_from_experience(self, experience: Dict) -> None:
        """从经验中学习"""
        self.experiences.append(experience)

        task_type = experience.get("task_type", "unknown")
        success = experience.get("success", False)
        self._success_history[task_type].append(1 if success else 0)

        if len(self._success_history[task_type]) > 100:
            self._success_history[task_type] = self._success_history[task_type][-100:]

        if "capability_used" in experience:
            cap = experience["capability_used"]
            current = self._capability_scores.get(cap, 0.5)
            adjustment = self.learning_rate * (1 if success else -0.5)
            self._capability_scores[cap] = max(0, min(1, current + adjustment))

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

        if reflection["score"] < 70:
            reflection["improvements"].append("考虑使用更好的策略")

        return reflection

    def optimize_self(self) -> Dict:
        """自我优化 - 基于历史表现调整参数"""
        success_rate = self._get_success_rate()
        optimizations = {}

        if success_rate > 0.8:
            old = self.confidence_threshold
            self.confidence_threshold = min(0.8, old + 0.05)
            optimizations["confidence_threshold"] = {"old": old, "new": self.confidence_threshold}
        elif success_rate < 0.5:
            old = self.confidence_threshold
            self.confidence_threshold = max(0.4, old - 0.05)
            optimizations["confidence_threshold"] = {"old": old, "new": self.confidence_threshold}

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

        # 1. 自我评估（由 LLM 完成）
        decision = self.can_handle(user_input, context)

        if not decision["can"]:
            # 尝试委托（由 LLM 完成）
            should_delegate, target = self.should_delegate(user_input, context)
            if should_delegate and target:
                return self._delegate_to(target, user_input)

        # 2. 任务分解（由 LLM 完成）
        if self._is_complex_task(user_input):
            subtasks = self.decompose_task(user_input, context)
            result = self._execute_with_subtasks(subtasks)
        else:
            result = self.process(user_input, context)

        # 3. 反思
        result["response_time"] = (time.time() - start_time) * 1000
        reflection = self.reflect_on_result(result)
        result["reflection"] = reflection

        # 4. 学习
        self.learn_from_experience({
            "input": user_input,
            "result": result.get("response", ""),
            "success": result.get("success", False),
            "task_type": self._classify_task_type_by_llm(user_input),
            "response_time": result["response_time"],
        })

        return result

    # ==================== 辅助方法 ====================

    def _get_specialties(self) -> List[str]:
        return [cap for cap, score in self._capability_scores.items() if score > 0.7]

    def _get_limitations(self) -> List[str]:
        return [cap for cap, score in self._capability_scores.items() if score < 0.3]

    def _get_success_rate(self) -> float:
        if self._performance_stats["total_tasks"] == 0:
            return 0.5
        return self._performance_stats["success_count"] / self._performance_stats["total_tasks"]

    def _classify_task_type_by_llm(self, user_input: str) -> str:
        """由 LLM 分类任务类型"""
        prompt = f"""分类任务类型，只输出一个关键词：coding/analysis/writing/chat/calculation

用户输入：{user_input[:100]}

输出：
"""
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 20, "temperature": 0.1}
                },
                timeout=10
            )
            if resp.status_code == 200:
                result = resp.json().get("response", "").strip().lower()
                if result in ["coding", "analysis", "writing", "chat", "calculation"]:
                    return result
        except:
            pass
        return "chat"

    def _is_complex_task(self, user_input: str) -> bool:
        """判断是否为复杂任务（简单规则保留，不影响 LLM 共生）"""
        complex_indicators = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        return len(user_input) > 50 or any(ind in user_input for ind in complex_indicators)

    def _execute_with_subtasks(self, subtasks: List[Dict]) -> Dict:
        """执行子任务链"""
        results = {}
        for subtask in subtasks:
            deps_satisfied = all(dep in results for dep in subtask.get("deps", []))
            if not deps_satisfied:
                continue
            result = self.process(subtask.get("description", subtask.get("action", "")), {})
            results[subtask.get("id", subtask.get("action", ""))] = result

        return {
            "success": True,
            "response": "\n".join([r.get("response", "") for r in results.values()]),
            "subtask_results": results,
        }

    def _delegate_to(self, target_agent: str, user_input: str) -> Dict:
        self.bus_publish(f"agent.{target_agent}.delegate", {"from": self.name, "input": user_input})
        return {
            "success": True,
            "response": f"我将把这个问题转交给 {target_agent} 处理。",
            "delegated_to": target_agent,
        }

    def _get_available_agents(self) -> List[str]:
        try:
            from core.lib.agent_registry import agent_registry
            return agent_registry.list_agents()
        except:
            return ["chat_agent", "code_agent"]

    # ==================== 经验管理 ====================

    def record_experience(self, experience: Dict) -> None:
        experience["timestamp"] = datetime.now().isoformat()
        self.experiences.append(experience)
        if len(self.experiences) > 100:
            self.experiences = self.experiences[-100:]

    def share_experience(self, target_agent: str, experience_id: int) -> bool:
        if experience_id >= len(self.experiences):
            return False
        self.bus_publish(f"agent.{target_agent}.experience", self.experiences[experience_id])
        return True

    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "total_tasks": self._performance_stats["total_tasks"],
            "success_rate": self._get_success_rate(),
            "avg_response_time": self._performance_stats["avg_response_time"],
            "experience_count": len(self.experiences),
            "capabilities": self._capability_descriptions,
            "specialties": self._get_specialties(),
        }

    def get_memory(self, key: str, default=None) -> Any:
        return self._memory.get(key, default)

    def set_memory(self, key: str, value) -> None:
        self._memory[key] = value

    def register_capability(self, capability: str, initial_score: float = 0.5):
        if capability not in self._capability_descriptions:
            self._capability_descriptions.append(capability)
        self._capability_scores[capability] = initial_score
        print(f"[{self.name}] 已注册能力: {capability}")

    def _load_intelligent_config(self):
        self.confidence_threshold = unified_config.get("smart.confidence_threshold", 0.6)
        self.learning_rate = unified_config.get("smart.learning_rate", 0.1)
        self.max_retries = unified_config.get("smart.max_retries", 2)
