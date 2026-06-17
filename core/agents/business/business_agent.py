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

from typing import Dict, Optional, Any, Tuple, List  # 添加 List
from abc import abstractmethod
import hashlib
import time
import re
import random
from datetime import datetime
from core.agents.base.smart_agent import SmartAgent
from core.agents.base.mixins.json_capable_mixin import JSONCapableMixin
from core.lib.federated.federated_learning import federated_learning
from core.lib.performance.optimizer import cache_manager, batch_processor, model_selector

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
            "model_used": {},
            "total_interactions": 0,  # 添加这行
        }
        #==========主动建议后台服务 ==========
        self._start_proactive_service()
        # 修复：正确的 getattr 语法
        agent_name = getattr(self, 'name', 'unknown')
        #==========联邦学习 ==========
        self._federated_enabled = True
        # 启动话本自动学习
        self._start_scriptbook_learning()
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
        user_lower = user_input.lower()
    
        # 科学计算任务 - 用最强模型
        science_keywords = ["sqrt", "sin", "cos", "tan", "log", "ln", "pi", 
                            "函数", "公式", "科学计算", "factorial", "导数", "积分",
                            "解方程", "求导", "微分"]
    
        if any(kw in user_lower for kw in science_keywords):
            # 优先使用 qwen2.5:7b（4.7GB）
            return "qwen2.5:7b"
    
        # 复杂计算任务
        complex_keywords = ["计算", "公式", "表达式", "括号", "幂", "平方"]
        if any(kw in user_lower for kw in complex_keywords) and len(user_input) > 30:
            return "qwen2.5:7b"
    
        # 代码相关任务 - 用 codellama
        code_keywords = ["代码", "编程", "函数", "算法", "写一个"]
        if any(kw in user_lower for kw in code_keywords):
            return "codellama:7b"
    
        # 一般任务 - 用 phi3 或 qwen2.5:3b
        if len(user_input) > 50:
            return "phi3:mini"
    
        # 默认使用最快的小模型
        return "qwen2:1.5b-instruct"


    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM - 带模型选择"""
        if not model:
            model = self._select_model(prompt)  
        # 对于简单对话，用最快模型
        if len(prompt) < 100 and "代码" not in prompt:
            model = "qwen2:1.5b-instruct"   
     
        # 添加 system prompt 固定身份
        system_prompt = "你是 ClawsJoy ChatAgent，一个智慧对话助手。你的身份是 ClawsJoy，不是其他模型。回答要简洁友好。"
        full_prompt = f"{system_prompt}\n\n用户: {prompt}\n助手:"

        try:
            import requests
        
            # 使用 Ollama API
            resp = requests.post(
                "http://localhost:11434/api/generate",  # 确保端口正确
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,  # 降低温度以获得更确定性的输出
                        "num_predict": 150  # 限制输出长度，防止编故事
                    }
                },
                timeout=60
            )
        
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "")
            else:
                print(f"[DEBUG] LLM 返回错误: {resp.status_code}")
        except Exception as e:
            print(f"[DEBUG] LLM 调用异常: {e}")
    
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
        # 增加交互计数
        self._stats["total_interactions"] = self._stats.get("total_interactions", 0) + 1
        # 生成缓存键
        cache_key = hashlib.md5(f"{user_input}:{self.name}".encode()).hexdigest()
    
        # 尝试从缓存获取
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
    
        # 执行
        result = self._execute_business(user_input, context)
    
        # 存入缓存
        cache_manager.set(cache_key, result)
    
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



    # ========== 主动建议能力 ==========

    def _get_proactive_suggestions(self, user_input: str = None) -> list:
        """获取主动建议列表"""
        suggestions = []
    
        # 1. 基于时间建议
        current_hour = datetime.now().hour
        if 6 <= current_hour < 9:
            suggestions.append("☀️ 早上好！需要我帮您规划今天的工作吗？")
        elif 11 <= current_hour < 14:
            suggestions.append("🍜 午饭时间到了，需要帮您推荐附近餐厅吗？")
        elif 21 <= current_hour < 23:
            suggestions.append("🌙 晚安！需要设置明早的提醒吗？")
    
        # 2. 基于未完成事项
        if hasattr(self, '_todos') and self._todos:
            pending = [t for t in self._todos if not t.get("completed", False)]
            if pending:
                suggestions.append(f"📋 您有 {len(pending)} 个待办未完成，需要处理吗？")
    
        # 3. 基于用户偏好
        user_name = self.recall_forever("user_name")
        if user_name and "建议" not in str(user_input):
            suggestions.append(f"💡 {user_name}，有什么我可以帮您的吗？")
    
        # 4. 基于对话历史（如果很久没聊）
        if hasattr(self, '_conversation_history') and len(self._conversation_history) > 10:
            suggestions.append("💬 您最近聊了很多，需要我帮您总结一下吗？")
    
        return suggestions[:3]  # 最多3条

    def add_proactive_hook(self):
        """添加主动服务钩子（在后台运行）"""
        import threading
    
        def _proactive_loop():
            while getattr(self, '_proactive_running', True):
                time.sleep(300)  # 每5分钟检查一次
                suggestions = self._get_proactive_suggestions()
                if suggestions:
                    # 触发主动推送（可以通过事件系统）
                    self._trigger_proactive_event(suggestions)
    
        self._proactive_running = True
        thread = threading.Thread(target=_proactive_loop, daemon=True)
        thread.start()
        print(f"✅ {self.name} 主动建议服务已启动")

    def _trigger_proactive_event(self, suggestions: list):
        """触发主动事件"""
        try:
            from core.lib.agent_communication import agent_communication
            agent_communication.publish("proactive.suggestion", {
                "agent": self.name,
                "user_id": self.user_id,
                "suggestions": suggestions,
                "timestamp": datetime.now().isoformat()
            })
        except ImportError:
            print(f"[Proactive] {self.name} 建议: {suggestions[0][:50]}...")
        except Exception as e:
            print(f"[Proactive] 事件触发失败: {e}")   

    # ========== 任务分解能力 ==========
    def decompose_task(self, task: str) -> Dict:
        """将复杂任务分解为子任务"""
        import json
    
        if self._is_simple_task(task):
            return {
                "sub_tasks": [{"id": 1, "action": "chat", "target": "text", "description": task, "depends_on": []}],
                "mode": "simple"
            }
    
        # 使用更严格的 system prompt 和 user prompt
        system_prompt = "你是一个任务分解专家。你必须只输出 JSON，不输出任何其他文字。"
    
        user_prompt = f"""将以下任务分解为子任务，只输出 JSON。

任务：{task}

输出格式（只输出这个 JSON，不要有其他文字）：
{{"sub_tasks": [{{"id": 1, "action": "analyze", "target": "data", "description": "描述", "depends_on": []}}], "mode": "sequential"}}

可用的 action: analyze, generate, send, search, calculate, translate, chat
可用的 target: data, chart, email, info, number, text, code

直接输出 JSON："""

        # 组合 prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
        response = self._call_llm(full_prompt)
    
        if response:
            response = response.strip()
        
            # 尝试多种方式提取 JSON
            json_str = None
        
            # 方法1: 直接解析
            try:
                json_str = json.loads(response)
            except:
                pass
        
            # 方法2: 提取 {...}
            if not json_str:
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    try:
                        json_str = json.loads(match.group())
                    except:
                        pass
        
            # 方法3: 使用规则分解
            if not json_str:
                print(f"[DEBUG] LLM 未返回有效 JSON，使用规则分解")
                return self._rule_based_decompose(task)
        
            if json_str.get("sub_tasks"):
                print(f"[DEBUG] 任务分解成功: {len(json_str['sub_tasks'])} 个子任务")
                return json_str
    
        return self._rule_based_decompose(task)



    def _rule_based_decompose(self, task: str) -> Dict:
        """基于规则的任务分解（降级方案）"""
        sub_tasks = []
    
        # 关键词到 action/target 的映射
        action_map = {
            "分析": ("analyze", "data"),
            "生成": ("generate", "chart"),
            "发送": ("send", "email"),
            "搜索": ("search", "info"),
            "计算": ("calculate", "number"),
            "翻译": ("translate", "text"),
            "写": ("generate", "code"),
        }
    
        # 按顺序拆分
        parts = re.split(r'然后|接着|之后|再', task)
    
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
        
            # 匹配动作
            action, target = "chat", "text"
            for kw, (act, tgt) in action_map.items():
                if kw in part:
                    action, target = act, tgt
                    break
        
            sub_tasks.append({
                "id": i + 1,
                "action": action,
                "target": target,
                "description": part,
                "depends_on": [i] if i > 0 else []
            })
    
        if not sub_tasks:
            sub_tasks = [{"id": 1, "action": "chat", "target": "text", "description": task, "depends_on": []}]
    
        return {
            "sub_tasks": sub_tasks,
            "mode": "sequential" if len(sub_tasks) > 1 else "simple"
        }

    def execute_decomposed_task(self, decomposition: Dict, context: Dict = None) -> Dict:
        """执行分解后的任务，调用不同 Agent"""
        results = []
        sub_tasks = decomposition.get("sub_tasks", [])
        mode = decomposition.get("mode", "sequential")
    
        # 构建依赖图
        task_map = {t["id"]: t for t in sub_tasks}
    
        if mode == "sequential":
            # 顺序执行
            for task in sub_tasks:
                result = self._execute_sub_task_with_agent(task, context)
                results.append(result)
                if context is not None:
                    context[f"task_{task['id']}_result"] = result
    
        elif mode == "parallel":
            # 并行执行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(sub_tasks)) as executor:
                futures = {
                    executor.submit(self._execute_sub_task_with_agent, task, context): task
                    for task in sub_tasks
                }
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results.append(result)
    
        elif mode == "dag":
            # DAG 执行（按依赖顺序）
            results = self._execute_dag_tasks(sub_tasks, task_map, context)
    
        # 合并结果
        return self._merge_results(results)

    def _execute_sub_task_with_agent(self, task: Dict, context: Dict = None) -> Dict:
        """使用专门的 Agent 执行子任务"""
        action = task.get("action", "chat")
        target = task.get("target", "text")
        description = task.get("description", "")
    
        # 根据 action 选择对应的 Agent
        agent_mapping = {
            ("analyze", "data"): "analysis_agent",
            ("generate", "code"): "code_agent",
            ("generate", "chart"): "code_agent",
            ("send", "email"): "chat_agent",
            ("search", "info"): "chat_agent",
            ("calculate", "number"): "calculator_agent",
            ("translate", "text"): "translate_agent",
        }
    
        agent_name = agent_mapping.get((action, target), "chat_agent")
    
        # 构建输入
        sub_input = description if description else f"{action} {target}"
    
        print(f"[DEBUG] 调用 {agent_name} 执行: {sub_input[:50]}...")
    
        # 获取 Agent 实例
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
                "raw_result": result
            }
    
        return {
            "task_id": task.get("id"),
            "action": action,
            "target": target,
            "agent": agent_name,
            "success": False,
            "output": f"无法执行：Agent {agent_name} 不可用",
            "error": "agent_not_available"
        }

    def _execute_dag_tasks(self, sub_tasks: List[Dict], task_map: Dict, context: Dict = None) -> List[Dict]:
        """执行 DAG 任务（按依赖顺序）"""
        from collections import deque
    
        # 计算入度
        in_degree = {}
        for task in sub_tasks:
            task_id = task["id"]
            in_degree[task_id] = len(task.get("depends_on", []))
    
        # 拓扑排序
        queue = deque([task_id for task_id, deg in in_degree.items() if deg == 0])
        results = []
        completed = set()
    
        while queue:
            task_id = queue.popleft()
            task = task_map[task_id]
        
            # 执行任务
            result = self._execute_sub_task_with_agent(task, context)
            results.append(result)
            completed.add(task_id)
        
            # 更新依赖
            for other in sub_tasks:
                if task_id in other.get("depends_on", []):
                    in_degree[other["id"]] -= 1
                    if in_degree[other["id"]] == 0:
                        queue.append(other["id"])
    
        return results

    def _merge_results(self, results: List[Dict]) -> Dict:
        """合并子任务结果"""
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)
    
        # 收集输出
        outputs = []
        for r in results:
            output = r.get("output", "")
            if output:
                outputs.append(f"【{r.get('agent', 'unknown')}】{output[:200]}")
    
        return {
            "success": success_count == total_count,
            "total_sub_tasks": total_count,
            "successful_sub_tasks": success_count,
            "results": results,
            "merged_output": "\n\n".join(outputs) if outputs else "所有子任务执行完成"
        }


    def _is_simple_task(self, task: str) -> bool:
        """判断是否为简单任务"""
        complex_indicators = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        return len(task) < 30 or not any(ind in task for ind in complex_indicators)

    def _simple_decompose(self, task: str) -> Dict:
        """简单任务分解（降级方案）"""
        return {
            "sub_tasks": [{"id": 1, "action": "process", "description": task}],
            "mode": "simple"
        }

    def execute_decomposed_task(self, decomposition: Dict, context: Dict = None) -> Dict:
        """执行分解后的任务"""
        results = []
        sub_tasks = decomposition.get("sub_tasks", [])
        mode = decomposition.get("mode", "sequential")
    
        if mode == "sequential":
            # 顺序执行
            for task in sub_tasks:
                result = self._execute_sub_task(task, context)
                results.append(result)
                # 更新上下文
                if context is not None:
                    context[f"task_{task['id']}_result"] = result
    
        elif mode == "parallel":
            # 并行执行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._execute_sub_task, task, context): task
                    for task in sub_tasks
                }
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results.append(result)
    
        # 合并结果
        return self._merge_results(results)

    def _execute_sub_task(self, task: Dict, context: Dict = None) -> Dict:
        """执行单个子任务"""
        action = task.get("action", "chat")
        target = task.get("target", "text")
        description = task.get("description", "")
    
        # 构建子任务输入
        sub_input = f"{action} {target}: {description}" if description else f"{action} {target}"
    
        # 调用相应 Agent
        if hasattr(self, '_execute_business'):
            return self._execute_business(sub_input, context)
    
        return {"success": False, "error": "无法执行子任务"}

    def _merge_results(self, results: List[Dict]) -> Dict:
        """合并子任务结果"""
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)
    
        # 收集输出内容
        outputs = []
        for r in results:
            content = r.get("response", r.get("output_content", ""))
            if content:
                outputs.append(content)
    
        return {
            "success": success_count == total_count,
            "total_sub_tasks": total_count,
            "successful_sub_tasks": success_count,
            "results": results,
            "merged_output": "\n\n".join(outputs) if outputs else ""
        }


    def _start_proactive_service(self):
        """启动主动建议后台服务"""
        import threading
        import time

        def _proactive_loop():
            print(f"🚀 [{self.name}] 主动建议服务已启动")
            from datetime import datetime
            while getattr(self, '_proactive_running', True):
                time.sleep(60)  # 每分钟检查一次
        
                try:
                    # 获取用户最后一条消息（从会话历史）
                    last_input = ""
                    if hasattr(self, '_conversation_history') and self._conversation_history:
                        last_input = self._conversation_history[-1].get("user", "")
            
                    # 传递参数
                    suggestions = self._get_proactive_suggestions(last_input)
                    if suggestions:
                        self._trigger_proactive_event(suggestions)
                except Exception as e:
                    print(f"主动服务错误: {e}")
        self._proactive_running = True
        thread = threading.Thread(target=_proactive_loop, daemon=True)
        thread.start()
    def share_experience(self, experience: Dict):
        """分享经验到联邦学习"""
        if not self._federated_enabled:
            return
    
        knowledge = {
            f"{experience.get('type', 'general')}": experience.get('result', '')
        }
        federated_learning.share_knowledge(self.name, knowledge, experience.get('confidence', 0.5))

    def query_peers(self, query: str) -> List[Dict]:
        """查询其他 Agent 的知识"""
        if not self._federated_enabled:
            return []
        return federated_learning.query_knowledge(self.name, query)



    def _start_scriptbook_learning(self):
        """启动话本自动学习线程"""
        import threading
        import time
    
        def learn_loop():
            while getattr(self, '_scriptbook_learning_running', True):
                time.sleep(3600)  # 每小时检查一次
                self._auto_learn_scriptbook()
    
        self._scriptbook_learning_running = True
        thread = threading.Thread(target=learn_loop, daemon=True)
        thread.start()

    def _auto_learn_scriptbook(self):
        """自动学习优化话本"""
        try:
            from core.lib.scriptbook_learner import scriptbook_learner
        
            scriptbook_learner.agent_name = self.name
            scriptbook_learner._load_stats()
            stats = scriptbook_learner.get_stats()
        
            # 命中率低于 60% 时需要优化
            if stats["hit_rate"] < 0.6 and stats["total_misses"] > 10:
                suggestions = stats.get("suggestions", [])
            
                if suggestions:
                    print(f"[{self.name}] 发现话本优化机会: {len(suggestions)} 个建议")
                    self._apply_scriptbook_suggestions(suggestions)
                
        except Exception as e:
            print(f"话本自动学习失败: {e}")

    def _apply_scriptbook_suggestions(self, suggestions: list):
        """应用话本建议"""
        import yaml
        from pathlib import Path
    
        script_path = Path(f"agents/{self.name}/scriptbook.yaml")
        if not script_path.exists():
            return
    
        with open(script_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    
        updated = False
        for sug in suggestions:
            new_intent = f"auto_{sug['type']}_{int(time.time())}"
            keywords = sug.get("suggested_keywords", [])
        
            # 检查是否已存在类似意图
            existing_keywords = []
            for intent in config.get("intents", []):
                existing_keywords.extend(intent.get("keywords", []))
        
            new_keywords = [k for k in keywords if k not in existing_keywords]
            if new_keywords:
                config.setdefault("intents", []).append({
                    "keywords": new_keywords[:3],
                    "response": new_intent
                })
                config.setdefault("templates", {})[new_intent] = f"用户提到了相关话题，需要友好回应。"
                updated = True
    
        if updated:
            with open(script_path, 'w') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            print(f"[{self.name}] 话本已自动更新")
        
            # 热重载
            if hasattr(self, '_load_scriptbook'):
                self._load_scriptbook()

    def _smart_fallback(self, user_input: str) -> str:
        """智能 fallback - 子类可覆盖"""
        from core.lib.smart_fallback import smart_fallback
        description = getattr(self, 'description', '智能助手')
        return smart_fallback(self.name, user_input, description)
