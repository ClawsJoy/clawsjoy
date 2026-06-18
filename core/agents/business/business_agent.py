#!/usr/bin/env python3
"""
BusinessAgent v4.1 - LLM-First 业务基类

特点:
1. 缓存、批处理优化（保留）
2. 模型选择由 LLM 评估
3. 任务分解由 LLM 完成
4. 主动建议由 LLM 生成
5. 6GB 显存优化
"""

from typing import Dict, Optional, Any, Tuple, List
from abc import abstractmethod
import hashlib
import time
import re
import json
from datetime import datetime
from core.agents.base.smart_agent import SmartAgent
from core.agents.base.mixins.json_capable_mixin import JSONCapableMixin
from core.lib.federated.federated_learning import federated_learning
from core.lib.performance.optimizer import cache_manager, batch_processor, model_selector


class BusinessAgent(SmartAgent, JSONCapableMixin):
    """
    LLM-First 业务基类
    """

    _CACHE_SIZE = 100
    _BATCH_SIZE = 8

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        JSONCapableMixin.__init__(self)

        self.engines = {}
        self._response_cache = {}
        self._embedding_cache = {}
        self._pending_tasks = []

        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "batch_processed": 0,
            "model_used": {},
            "total_interactions": 0,
        }

        self._federated_enabled = True

        agent_name = getattr(self, 'name', 'unknown')
        print(f"🧠 BusinessAgent v4.1 初始化: {agent_name}")

    # ========== 缓存（保留）==========

    def _get_cache_key(self, user_input: str, context: Dict = None) -> str:
        key = user_input[:200]
        if context:
            key += str(sorted(context.items()))[:100]
        return hashlib.md5(key.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        if key in self._response_cache:
            self._stats["cache_hits"] += 1
            return self._response_cache[key]
        self._stats["cache_misses"] += 1
        return None

    def _save_to_cache(self, key: str, result: Dict):
        self._response_cache[key] = result
        if len(self._response_cache) > self._CACHE_SIZE:
            oldest = next(iter(self._response_cache))
            del self._response_cache[oldest]

    # ========== 批处理（保留）==========

    def add_to_batch(self, user_input: str, callback=None):
        self._pending_tasks.append({"input": user_input, "callback": callback, "timestamp": time.time()})
        if len(self._pending_tasks) >= self._BATCH_SIZE:
            self._process_batch()

    def _process_batch(self):
        if not self._pending_tasks:
            return

        batch = self._pending_tasks[:self._BATCH_SIZE]
        self._pending_tasks = self._pending_tasks[self._BATCH_SIZE:]

        inputs = [t["input"] for t in batch]
        if hasattr(self, '_execute_batch'):
            results = self._execute_batch(inputs)
        else:
            results = [self._execute_business(inp, None) for inp in inputs]

        self._stats["batch_processed"] += len(batch)

        for task, result in zip(batch, results):
            if task["callback"]:
                task["callback"](result)

        return results

    # ========== LLM-First 模型选择 ==========

    def _select_model(self, user_input: str) -> str:
        """由 LLM 评估任务复杂度，选择模型"""
        prompt = f"""评估以下任务的复杂度，只输出一个关键词：light/medium/heavy

用户输入：{user_input[:200]}

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
                    "options": {"num_predict": 10, "temperature": 0.1}
                },
                timeout=10
            )
            if resp.status_code == 200:
                result = resp.json().get("response", "").strip().lower()
                if result == "heavy":
                    return "qwen2.5:7b"
                elif result == "medium":
                    return "qwen2.5:3b"
        except:
            pass

        # 降级：按长度
        if len(user_input) > 100:
            return "qwen2.5:3b"
        return "qwen2:1.5b-instruct"

    def _call_llm(self, prompt: str, model: str = None) -> str:
        if not model:
            model = self._select_model(prompt)

        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 150}
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[DEBUG] LLM 调用异常: {e}")

        return ""

    # ========== 核心方法 ==========

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return False, 0.0

    @abstractmethod
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        pass

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        self._stats["total_interactions"] = self._stats.get("total_interactions", 0) + 1
        cache_key = hashlib.md5(f"{user_input}:{self.name}".encode()).hexdigest()

        cached = cache_manager.get(cache_key)
        if cached:
            return cached

        result = self._execute_business(user_input, context)
        cache_manager.set(cache_key, result)

        return result

    def handle(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        return self.process(user_input, context)

    def get_stats(self) -> Dict:
        stats = super().get_stats() if hasattr(super(), 'get_stats') else {}
        cache_hits = self._stats.get('cache_hits', 0)
        cache_misses = self._stats.get('cache_misses', 0)
        total = cache_hits + cache_misses
        cache_hit_rate = cache_hits / total if total > 0 else 0

        stats.update({
            "business": self._stats,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses
        })
        return stats

    # ========== 主动建议（由 LLM 生成）==========

    def _get_proactive_suggestions(self, user_input: str = None) -> list:
        """由 LLM 生成主动建议"""
        if not user_input:
            return []

        prompt = f"""根据用户历史对话，生成 2-3 条主动建议。

用户最近说：{user_input[:200]}

输出格式：每条建议一行，不要编号。
"""
        try:
            response = self._call_llm(prompt)
            if response:
                suggestions = [s.strip() for s in response.split('\n') if s.strip()]
                return suggestions[:3]
        except:
            pass

        return ["💡 有什么我可以帮您的吗？"]

    # ========== 任务分解（由 LLM 完成）==========

    def decompose_task(self, task: str, context: Dict = None) -> Dict:
        """由 LLM 动态分解任务"""
        prompt = f"""将以下任务分解为子任务，输出 JSON。

任务：{task}

输出格式：
{{"sub_tasks": [{{"id": 1, "action": "analyze", "target": "data", "description": "描述", "depends_on": []}}], "mode": "sequential"}}

可用的 action: analyze, generate, search, calculate, translate, chat, write, review, fix

只输出 JSON：
"""
        try:
            response = self._call_llm(prompt)
            if response:
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                    if result.get("sub_tasks"):
                        return result
        except Exception as e:
            print(f"[DEBUG] 任务分解失败: {e}")

        # 降级：单任务
        return {"sub_tasks": [{"id": 1, "action": "process", "target": "task", "description": task, "depends_on": []}], "mode": "simple"}

    def execute_decomposed_task(self, decomposition: Dict, context: Dict = None) -> Dict:
        """执行分解后的任务"""
        results = []
        sub_tasks = decomposition.get("sub_tasks", [])
        mode = decomposition.get("mode", "sequential")

        if mode == "sequential":
            for task in sub_tasks:
                result = self._execute_sub_task_with_agent(task, context)
                results.append(result)
        elif mode == "parallel":
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(sub_tasks)) as executor:
                futures = {executor.submit(self._execute_sub_task_with_agent, task, context): task for task in sub_tasks}
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

        return self._merge_results(results)

    def _execute_sub_task_with_agent(self, task: Dict, context: Dict = None) -> Dict:
        action = task.get("action", "chat")
        target = task.get("target", "text")
        description = task.get("description", "")

        agent_mapping = {
            ("analyze", "data"): "analysis_agent",
            ("generate", "code"): "code_agent",
            ("calculate", "number"): "calculator_agent",
            ("translate", "text"): "translate_agent",
        }

        agent_name = agent_mapping.get((action, target), "chat_agent")
        sub_input = description if description else f"{action} {target}"

        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            sub_agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
            if sub_agent:
                result = sub_agent.process(sub_input)
                return {
                    "task_id": task.get("id"),
                    "action": action,
                    "target": target,
                    "agent": agent_name,
                    "success": result.get("success", False),
                    "output": result.get("response", result.get("output_content", "")),
                }
        except Exception as e:
            print(f"[DEBUG] 子任务执行失败: {e}")

        return {"task_id": task.get("id"), "action": action, "target": target, "agent": agent_name, "success": False, "output": f"执行失败: {e}"}

    def _merge_results(self, results: List[Dict]) -> Dict:
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)

        outputs = []
        for r in results:
            content = r.get("output", "")
            if content:
                outputs.append(content)

        return {
            "success": success_count == total_count,
            "total_sub_tasks": total_count,
            "successful_sub_tasks": success_count,
            "results": results,
            "merged_output": "\n\n".join(outputs) if outputs else "",
        }

    # ========== 联邦学习 ==========

    def share_experience(self, experience: Dict):
        if not self._federated_enabled:
            return
        knowledge = {f"{experience.get('type', 'general')}": experience.get('result', '')}
        federated_learning.share_knowledge(self.name, knowledge, experience.get('confidence', 0.5))

    def query_peers(self, query: str) -> List[Dict]:
        if not self._federated_enabled:
            return []
        return federated_learning.query_knowledge(self.name, query)
