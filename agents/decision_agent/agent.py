
import os
import sys

    with open("/tmp/decision_debug.log", "a") as f:
        f.write(f"{msg}\n")
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

import sys
sys.stdout = sys.stderr

"""DecisionAgent - 决策者 v5.3.0 (修复初始化顺序)"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

import atexit
import concurrent.futures
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from core.agents.business.base_business_agent import BusinessAgent


@dataclass
class DecisionRecord:
    task: str
    decision: str
    result: str
    confidence: float
    timestamp: str
    context: Dict = field(default_factory=dict)


class DecisionAgent(BusinessAgent):
    """决策者 - 多源综合决策 (v5.3.0)"""

    name = "decision_agent"
    description = "智能决策者 - 多源综合决策"
    version = "5.3.0"

    # 可配置参数
    CACHE_TTL_SECONDS = 60
    EVIDENCE_TIMEOUT_SECONDS = 5.0
    THREAD_POOL_WORKERS = 3

    WEIGHTS = {
        "analyst": 0.45,
        "semantic": 0.20,
        "llm": 0.20,
        "historical": 0.10,
        "heuristic": 0.05,
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)

        # 1. 初始化基础属性（先于加载记忆）
        self._init_components()

        # 2. 缓存
        self._decision_cache = {}
        self._analysis_cache = {}
        self._route_stats = {"A": 0, "B": 0, "C": 0}

        # 3. 线程池（用于异步证据收集）
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.THREAD_POOL_WORKERS, thread_name_prefix="dec_"
        )

        # 4. 注册退出时清理
        atexit.register(self._cleanup)

        # 5. 加载历史记忆（此时属性已存在）
        self._load_memory()

        print(
            f"🎖️ 决策者 v{self.version} 已上岗 (经验记忆: {len(self._decision_memory)}条)"
        )

    def _init_components(self):
        """初始化组件（不依赖顺序）"""
        # 推理引擎
        try:
            from engine.reasoning import reasoning_engine

            self.reasoning_engine = reasoning_engine
        except:
            self.reasoning_engine = None

        # 语义引擎
        try:
            from engine.semantic import semantic_engine

            self.semantic_engine = semantic_engine
        except:
            self.semantic_engine = None

        # 决策记忆（先初始化为空列表）
        self._decision_memory: List[DecisionRecord] = []

    def _cleanup(self):
        """清理资源"""
        if hasattr(self, "_executor") and self._executor:
            self._executor.shutdown(wait=False)

    def _load_memory(self):
        """加载历史决策记忆"""
        try:
            import json
            from pathlib import Path

            memory_file = Path(f"data/users/{self.user_id}/decision_memory.json")
            if memory_file.exists():
                with open(memory_file) as f:
                    data = json.load(f)
                    for item in data[-100:]:
                        self._decision_memory.append(DecisionRecord(**item))
        except Exception as e:

    def _save_memory(self):
        """保存决策记忆"""
        try:
            import json
            from pathlib import Path

            memory_file = Path(f"data/users/{self.user_id}/decision_memory.json")
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(memory_file, "w") as f:
                json.dump([vars(r) for r in self._decision_memory[-200:]], f, indent=2)
        except:
            pass

    def process(self, user_input: str, context: dict = None) -> dict:
        return self._decide_and_route(user_input, context)

    def _execute_business(self, user_input: str, context: dict = None) -> dict:
        return self._decide_and_route(user_input, context)

    # ========== 缓存方法 ==========
    def _get_cache_key(self, user_input: str) -> str:
        return user_input[:100].strip().lower()

    def _get_cached_decision(self, cache_key: str):
        if cache_key in self._decision_cache:
            result, timestamp = self._decision_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.CACHE_TTL_SECONDS):
                return result
            else:
                del self._decision_cache[cache_key]
        return None

    def _cache_decision(self, cache_key: str, route_result: dict):
        # 限制缓存大小
        if len(self._decision_cache) > 500:
            # 删除最旧的条目
            oldest = min(
                self._decision_cache.keys(), key=lambda k: self._decision_cache[k][1]
            )
            del self._decision_cache[oldest]
        self._decision_cache[cache_key] = (route_result, datetime.now())

    # ========== 异步证据收集 ==========
    def _gather_evidences_async(self, user_input: str, context: dict = None) -> Dict:
        evidences = {"heuristic": self._get_heuristic_score(user_input)}
        futures = {}

        futures["analyst"] = self._executor.submit(
            self._get_analyst_report, user_input, context
        )

        if hasattr(self, "semantic_engine") and self.semantic_engine:
            futures["semantic"] = self._executor.submit(
                self._get_semantic_suggestion, user_input
            )

        if self._decision_memory:
            futures["historical"] = self._executor.submit(
                self._get_historical_suggestion, user_input
            )

        for key, future in futures.items():
            try:
                result = future.result(timeout=5.0)
                if result:
                    evidences[key] = result
            except concurrent.futures.TimeoutError:
            except Exception as e:

        return evidences

    # ========== 核心决策 ==========
    def _decide_and_route(self, user_input: str, context: dict = None) -> dict:

        # 检查缓存
        cache_key = self._get_cache_key(user_input)
        cached = self._get_cached_decision(cache_key)
        if cached:
            return cached

        # 异步收集证据
        evidences = self._gather_evidences_async(user_input, context)

        # 综合决策
        decision, confidence, reasoning, scores = self._make_decision(evidences)


        # 记录和路由
        self._record_decision(user_input, decision, confidence)
        self._route_stats[decision] = self._route_stats.get(decision, 0) + 1
        route_result = self._route(decision, user_input)

        if isinstance(route_result, dict):
            route_result["decision_metadata"] = {
                "decision": decision,
                "confidence": confidence,
                "reasoning": reasoning,
                "scores": scores,
                "route_stats": self._route_stats,
            }

        # 缓存结果
        self._cache_decision(cache_key, route_result)

        return route_result

    # ========== 证据收集方法 ==========
    def _get_analyst_report(self, user_input: str, context: dict = None) -> dict:
        try:
            from agents.analysis_agent.agent import analysis_agent

            report = analysis_agent.process(
                user_input, {"mode": "understanding", "caller": "decision_agent"}
            )
            if isinstance(report, dict):
                return {
                    "suggested_route": report.get("suggested_route", "C"),
                    "confidence": report.get("confidence", 0.8),
                }
        except Exception as e:
        return None

    def _get_semantic_suggestion(self, user_input: str) -> Optional[dict]:
        if not self.semantic_engine:
            return None
        try:
            result = self.semantic_engine.understand(user_input)
            # 基于原子引擎 intent 智能路由
            if result.intent == "translate":
                suggestion = "C"
            elif "翻译" in user_input.lower() and len(user_input) < 50:
                suggestion = "B"
            elif result.intent in ["chat", "greeting", "farewell", "thanks"]:
                suggestion = "A"
            elif result.intent in ["calculate", "weather"]:
                suggestion = "B"
            elif result.intent in ["code", "ai", "analysis"]:
                suggestion = "C"
            else:
                suggestion = "A"
            return {"suggestion": suggestion, "confidence": result.confidence}
        except:
            return None

    def _get_historical_suggestion(self, user_input: str) -> Optional[str]:
        if not self._decision_memory:
            return None
        success_decisions = []
        for record in self._decision_memory:
            if record.result == "success":
                if any(
                    kw in record.task for kw in user_input.split()[:3] if len(kw) > 2
                ):
                    success_decisions.append(record.decision)
        if success_decisions:
            from collections import Counter

            return Counter(success_decisions).most_common(1)[0][0]
        return None

    def _get_heuristic_score(self, user_input: str) -> float:
        score = 0.0
        lower_input = user_input.lower()
        if "翻译" in lower_input:
            score += 0.5
        if len(user_input) > 100:
            score += 0.3
        if any(kw in lower_input for kw in ["分析", "总结", "报告", "写"]):
            score += 0.4
        return min(score, 1.0)

    def _make_decision(self, evidences: Dict) -> Tuple[str, float, str, Dict]:
        scores = {"A": 0.0, "B": 0.0, "C": 0.0}
        reasoning_parts = []

        if evidences.get("analyst"):
            route = evidences["analyst"].get("suggested_route", "C")
            conf = evidences["analyst"].get("confidence", 0.8)
            scores[route] += self.WEIGHTS["analyst"] * conf
            reasoning_parts.append(f"分析师:{route}")

        if evidences.get("semantic"):
            route = evidences["semantic"].get("suggestion", "A")
            conf = evidences["semantic"].get("confidence", 0.7)
            scores[route] += self.WEIGHTS["semantic"] * conf
            reasoning_parts.append(f"语义:{route}")

        if evidences.get("historical"):
            route = evidences["historical"]
            scores[route] += self.WEIGHTS["historical"]
            reasoning_parts.append(f"历史:{route}")

        if evidences.get("heuristic", 0) > 0:
            scores["B"] += self.WEIGHTS["heuristic"] * evidences["heuristic"]
            reasoning_parts.append(f"启发:B")

        best_decision = max(scores, key=scores.get)
        best_score = scores[best_decision]
        reasoning = " | ".join(reasoning_parts)

        print(
            f"[决策者] 评分: A={scores['A']:.2f}, B={scores['B']:.2f}, C={scores['C']:.2f}"
        )

        return best_decision, best_score, reasoning, scores

    def _record_decision(self, task: str, decision: str, confidence: float):
        record = DecisionRecord(
            task=task[:200],
            decision=decision,
            result="pending",
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            context={},
        )
        self._decision_memory.append(record)
        self._save_memory()

    def _update_memory(self, task: str, decision: str, success: bool):
        for record in reversed(self._decision_memory):
            if record.task == task[:200] and record.decision == decision:
                record.result = "success" if success else "failed"
                break
        self._save_memory()

    def _route(self, decision: str, user_input: str) -> dict:
        if decision == "A":
            from agents.chat_agent.agent import chat_agent

            return chat_agent.process(user_input)
        elif decision == "B":
            from agents.executor_agent.agent import executor_agent

            return executor_agent.process(user_input)
        else:
            from agents.orchestrator.agent import orchestrator_agent

            return orchestrator_agent.process(user_input, {"caller": "decision_agent"})

    # ========== 状态查询 ==========
    def get_stats(self) -> dict:
        total = sum(self._route_stats.values())
        return {
            "total_decisions": total,
            "routes": self._route_stats,
            "distribution": {
                k: v / total if total > 0 else 0 for k, v in self._route_stats.items()
            },
            "cache_size": len(self._decision_cache),
            "memory_count": len(self._decision_memory),
        }


    def _get_semantic_suggestion(self, user_input: str) -> Optional[dict]:
        if not self.semantic_engine:
            return None
        try:
            result = self.semantic_engine.understand(user_input)
            # 基于原子引擎 intent 智能路由
            if result.intent == "translate":
                suggestion = "C"
            elif "翻译" in user_input.lower() and len(user_input) < 50:
                suggestion = "B"
            elif result.intent in ["chat", "greeting", "farewell", "thanks"]:
                suggestion = "A"
            elif result.intent in ["calculate", "weather"]:
                suggestion = "B"
            elif result.intent in ["code", "ai", "analysis"]:
                suggestion = "C"
            else:
                suggestion = "A"
            return {"suggestion": suggestion, "confidence": result.confidence}
        except Exception as e:
            return None

    def _get_semantic_suggestion(self, user_input: str) -> Optional[dict]:
        if not self.semantic_engine:
            return None
        try:
            result = self.semantic_engine.understand(user_input)
            
            # 强制覆盖：包含"翻译"关键词时，按长度判断路由
            if "翻译" in user_input:
                if len(user_input) > 20:
                    suggestion = "C"
                else:
                    suggestion = "B"
            elif result.intent in ["chat", "greeting", "farewell", "thanks"]:
                suggestion = "A"
            elif result.intent in ["calculate", "weather"]:
                suggestion = "B"
            elif result.intent in ["code", "ai", "analysis", "translate"]:
                suggestion = "C"
            else:
                suggestion = "A"
            
            return {"suggestion": suggestion, "confidence": result.confidence}
        except Exception as e:
            return None

decision_agent = DecisionAgent()
