# core/agents/business/business_agent.py
#!/usr/bin/env python3
"""
BusinessAgent v4.0 - 合并后的统一业务基类

特点:
1. 继承 SmartAgent + JSONCapableMixin
2. 集成 BusinessAgentV2 的引擎能力
3. 提供标准化 JSON 处理
4. 支持简单/复杂任务自动判断
5. 6GB 显存优化（小模型优先、缓存优先）

业务 Agent 基类 - 统一版本

职责分离:
- handle_json(): 处理标准化 JSON 输入 (新增)
- handle(): 处理自然语言输入 (保留兼容)
- process(): 底层业务逻辑 (子类实现)
"""

from typing import Dict, Optional, Any, Tuple
from abc import abstractmethod
import hashlib
import time

from core.agents.base.smart_agent import SmartAgent
from core.agents.base.mixins.json_capable_mixin import JSONCapableMixin


class BusinessAgent(SmartAgent, JSONCapableMixin):
    """
    业务 Agent 基类 - 统一版 v4.0
    
    使用方式:
        class MyAgent(BusinessAgent):
            def can_handle_json(self, action, target):
                return action == "my_action", 0.95
            
            def _execute_business(self, user_input, context):
                return {"response": "处理结果"}
    
    方法层次:
    ┌─────────────────────────────────────────────────────────────┐
    │  handle_json(json)  ← 入口1: 标准化 JSON (优先)              │
    │      ↓                                                      │
    │  handle(text)       ← 入口2: 自然语言 (兼容)                 │
    │      ↓                                                      │
    │  _execute_business(text) ← 核心业务逻辑 (子类实现)           │
    │      ↓                                                      │
    │  process(text)      ← 底层方法 (可选覆盖)                    │
    └─────────────────────────────────────────────────────────────┘
    """
    
    # 6GB 显存优化配置
    _CACHE_SIZE = 100          # 缓存大小
    _BATCH_SIZE = 8            # 动态批处理大小
    _SMALL_MODEL = "qwen2.5:1.5b"   # 简单任务用小模型
    _LARGE_MODEL = "qwen2.5:7b"     # 复杂任务用大模型
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        
        # 初始化 JSON 能力
        JSONCapableMixin.__init__(self)
        
        # ========== 引擎初始化（从 V2 合并）==========
        self.engines = {}
        
        # ========== 缓存（6GB 优化）==========
        self._response_cache = {}
        self._embedding_cache = {}
        
        # ========== 任务队列（批处理）==========
        self._pending_tasks = []
        
        # ========== 统计 ==========
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "batch_processed": 0,
            "model_used": {}
        }
        
        # 修复：正确的 getattr 语法
        agent_name = getattr(self, 'name', 'unknown')
        print(f"🧠 BusinessAgent v4.0 初始化: {agent_name}")
        print(f"   💾 缓存大小: {self._CACHE_SIZE}")
        print(f"   📦 批处理大小: {self._BATCH_SIZE}")
    
    # ========== 引擎初始化 ==========
    
    def _init_engines(self):
        """初始化横向引擎"""
        self.engines = {}
        self._init_semantic()
        self._init_knowledge()
        self._init_reasoning()
    
    def _init_semantic(self):
        try:
            from engine.semantic import semantic_engine
            self.engines["semantic"] = semantic_engine
        except:
            pass
    
    def _init_knowledge(self):
        try:
            from engine.knowledge import knowledge_engine
            self.engines["knowledge"] = knowledge_engine
        except:
            pass
    
    def _init_reasoning(self):
        try:
            from engine.reasoning import reasoning_engine
            self.engines["reasoning"] = reasoning_engine
        except:
            pass
    
    def get_engine(self, name: str):
        return self.engines.get(name)
    
    # ========== 缓存优化（6GB 显存）==========
    
    def _get_cache_key(self, user_input: str, context: Dict = None) -> str:
        """生成缓存键"""
        key = user_input[:200]
        if context:
            key += str(sorted(context.items()))[:100]
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """从缓存获取"""
        if key in self._response_cache:
            self._stats["cache_hits"] += 1
            return self._response_cache[key]
        self._stats["cache_misses"] += 1
        return None
    
    def _save_to_cache(self, key: str, result: Dict):
        """保存到缓存"""
        self._response_cache[key] = result
        # LRU 淘汰
        if len(self._response_cache) > self._CACHE_SIZE:
            oldest = next(iter(self._response_cache))
            del self._response_cache[oldest]
    
    # ========== 批处理 ==========
    
    def add_to_batch(self, user_input: str, callback=None):
        """添加到批处理队列"""
        self._pending_tasks.append({
            "input": user_input,
            "callback": callback,
            "timestamp": time.time()
        })
        
        if len(self._pending_tasks) >= self._BATCH_SIZE:
            self._process_batch()
    
    def _process_batch(self):
        """批量处理"""
        if not self._pending_tasks:
            return
        
        batch = self._pending_tasks[:self._BATCH_SIZE]
        self._pending_tasks = self._pending_tasks[self._BATCH_SIZE:]
        
        inputs = [t["input"] for t in batch]
        
        # 批量调用
        if hasattr(self, '_execute_batch'):
            results = self._execute_batch(inputs)
        else:
            results = [self._execute_business(inp, None) for inp in inputs]
        
        self._stats["batch_processed"] += len(batch)
        
        # 回调
        for task, result in zip(batch, results):
            if task["callback"]:
                task["callback"](result)
        
        return results
    
    # ========== 模型选择（6GB 优化）==========
    
    def _select_model(self, user_input: str) -> str:
        """根据任务复杂度选择模型"""
        # 简单任务用小模型
        if len(user_input) < 50:
            return "qwen2.5:3b"  # 改为存在的模型
        # 代码或复杂任务用大模型
        elif any(kw in user_input for kw in ["代码", "分析", "总结", "复杂"]):
            return "qwen2:7b-instruct"  # 改为存在的模型
        
        return "qwen2.5:3b"
        
            
    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM（带模型选择）"""
        if not model:
            model = self._select_model(prompt)
        
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=120  # 从 60 改为 120
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"LLM 调用失败: {e}")
        return ""
    
    # ========== 核心方法 ==========
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        """
        判断是否能处理（子类覆盖）
        返回: (能否处理, 置信度)
        """
        return False, 0.0
    
    @abstractmethod
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        核心业务逻辑（子类必须实现）
        """
        pass
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        处理入口（自动使用缓存、批处理）
        """
        # 检查缓存
        cache_key = self._get_cache_key(user_input, context)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # 执行
        result = self._execute_business(user_input, context)
        
        # 保存缓存
        self._save_to_cache(cache_key, result)
        
        return result
    
    def handle(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        自然语言入口（兼容）
        """
        return self.process(user_input, context)
    
        
    # ========== 统计 ==========
    
    def get_stats(self) -> Dict:
        """获取统计"""
        stats = super().get_stats() if hasattr(super(), 'get_stats') else {}
    
        # 计算缓存命中率
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
