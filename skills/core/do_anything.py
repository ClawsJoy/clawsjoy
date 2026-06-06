#!/usr/bin/env python3
"""大脑调度器 v5.0.0 - 配置驱动路由器"""

import yaml
from pathlib import Path
from datetime import datetime
from core.lib.unified_config import unified_config


class DoAnythingSkill:
    """
    大脑调度器 - 配置驱动路由器
    职责：根据 brain_rules.yaml 将任务路由到对应执行器
    """

    name = "do_anything"
    description = "智能大脑：配置驱动的任务路由"
    version = "5.0.0"
    category = "orchestrator"

    def __init__(self):
        self._load_config()
        self._load_executors()

    def _load_config(self):
        """加载路由配置"""
        config_file = Path("config/brain_rules.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {"priority": []}
        print(f"📋 加载路由配置，共 {len(self.config.get('priority', []))} 条规则")

    def _load_executors(self):
        """加载执行器"""
        self.executors = {}
        executors_config = self.config.get("executors", {})

        for name, exec_config in executors_config.items():
            if not exec_config.get("enabled", True):
                continue

            module_path = exec_config.get("module")
            if module_path:
                try:
                    module = __import__(module_path, fromlist=[''])
                    # 尝试获取 executor 实例
                    executor_name = exec_config.get("class", name)
                    if hasattr(module, executor_name):
                        self.executors[name] = getattr(module, executor_name)
                    elif hasattr(module, name):
                        self.executors[name] = getattr(module, name)
                    else:
                        # 尝试直接导入模块（如果是函数模块）
                        self.executors[name] = module
                    print(f"✅ 加载执行器: {name}")
                except Exception as e:
                    print(f"⚠️ 加载执行器 {name} 失败: {e}")

    def execute(self, params):
        """执行路由"""
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}

        print(f"🧠 [大脑 v{self.version}] 收到任务: {goal[:100]}")

        # 快速数学计算（特殊处理）
        import re
        math_match = re.search(r'(\d+)\s*([+\-*/xX])\s*(\d+)', goal)
        if math_match:
            try:
                a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
                if op in ['x', 'X']:
                    op = '*'
                result = eval(f"{a}{op}{b}")
                return self._format_response({"success": True, "result": result}, "math", goal)
            except:
                pass

        # 按优先级路由
        priority = self.config.get("priority", [])
        for rule in priority:
            handler_name = rule.get("handler")

            # 检查是否匹配
            if not self._match_rule(goal, rule):
                continue

            print(f"🎯 匹配到规则: {rule.get('name')} -> {handler_name}")

            # 获取执行器
            executor = self.executors.get(handler_name)
            if not executor:
                print(f"⚠️ 执行器未找到: {handler_name}")
                continue

            # 准备参数
            exec_params = {"goal": goal, "context": params.get("context", {})}

            # 执行
            try:
                if hasattr(executor, 'execute'):
                    result = executor.execute(goal, exec_params)
                elif callable(executor):
                    result = executor(goal, exec_params)
                else:
                    result = {"success": False, "error": f"执行器 {handler_name} 不可调用"}

                if result.get("success"):
                    return self._format_response(result, rule.get("name"), goal)
                else:
                    print(f"⚠️ 执行器 {handler_name} 失败: {result.get('error')}")
                    continue
            except Exception as e:
                print(f"⚠️ 执行器 {handler_name} 异常: {e}")
                continue

        # 兜底：LLM 执行器
        llm_executor = self.executors.get("llm_executor")
        if llm_executor:
            try:
                result = llm_executor.execute(goal, {"goal": goal})
                return self._format_response(result, "llm", goal)
            except Exception as e:
                return self._format_response({"success": False, "error": str(e)}, "error", goal)

        return self._format_response(
            {"success": False, "error": "无法处理该任务"},
            "error", goal
        )

    def _match_rule(self, goal: str, rule: dict) -> bool:
        """检查规则是否匹配"""
        # 检查关键词
        keywords = rule.get("keywords", [])
        if keywords:
            for keyword in keywords:
                if keyword in goal:
                    return True
            return False

        # 检查正则模式
        pattern = rule.get("pattern")
        if pattern:
            import re
            if re.search(pattern, goal):
                return True

        # 默认规则（兜底）
        return rule.get("default", False)

    def _format_response(self, result: dict, source: str, original_goal: str) -> dict:
        """格式化响应"""
        response = {
            "success": result.get("success", True),
            "source": source,
            "original_goal": original_goal,
            "timestamp": datetime.now().isoformat(),
        }

        if "result" in result:
            response["result"] = result["result"]
        if "response" in result:
            response["response"] = result["response"]
        if "error" in result:
            response["error"] = result["error"]

        return response


    def _get_cached_result(self, goal):
        """缓存执行结果"""
        import hashlib
        key = hashlib.md5(goal.encode()).hexdigest()
        # 简单缓存逻辑
        return None
    

    def _smart_fallback(self, goal: str) -> dict:
        """智能兜底：调用原子引擎"""
        try:
            from engine.semantic import semantic_engine
            result = semantic_engine.understand(goal)
            # 根据意图和置信度处理
            if result.confidence > 0.6:
                # 高置信度，使用 LLM 生成响应
                response = smart_adapter.generate(goal, auto_select=True)
                return {"success": True, "response": response, "source": "atomic_llm"}
            else:
                # 低置信度，返回通用提示
                return {
                    "success": True, 
                    "response": f"收到您的请求：{goal}。如需帮助，请更具体地描述。",
                    "source": "atomic_fallback"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_knowledge(self, query: str) -> str:
        """调用知识引擎检索"""
        try:
            from engine.knowledge import knowledge_engine
            results = knowledge_engine.query(query)
            if results:
                return results[0].get("content", "")[:500]
        except:
            pass
        return ""


    def _get_memory(self, key: str) -> str:
        """获取记忆"""
        try:
            from engine.memory import memory_engine
            return memory_engine.recall(key)
        except Exception as e:
            print(f"记忆引擎失败: {e}")
        return ""

    def _reason(self, query: str) -> dict:
        """逻辑推理"""
        try:
            from engine.reasoning import reasoning_engine
            decision, confidence, reasoning = reasoning_engine.process(query); return {"decision": decision, "confidence": confidence, "reasoning": reasoning}
        except Exception as e:
            print(f"推理引擎失败: {e}")
        return {}

    def _smart_route(self, goal: str) -> dict:
        """智能路由 - 集成多引擎"""
        try:
            # 1. 情感分析
            from engine.emotion import emotion_engine
            emotion = emotion_engine.analyze(goal)
            
            # 2. 语义理解
            from engine.semantic import semantic_engine
            semantic = semantic_engine.understand(goal)
            
            # 3. 知识检索
            knowledge = self._search_knowledge(goal)
            
            # 4. 记忆召回
            memory = self._get_memory(goal[:50])
            
            # 5. 推理
            from engine.reasoning import reasoning_engine
            reasoning = reasoning_engine.process({"input": goal})
            
            # 综合响应
            response = f"语义: {semantic.intent}\n"
            if knowledge:
                response += f"知识: {knowledge[:100]}\n"
            if memory:
                response += f"记忆: {memory}\n"
            response += f"情感: {emotion.get('dominant_emotion', 'neutral')}"
            
            return {
                "success": True,
                "response": response,
                "source": "multi_engine",
                "metadata": {
                    "intent": semantic.intent,
                    "confidence": semantic.confidence,
                    "emotion": emotion.get('dominant_emotion'),
                    "reasoning": reasoning[0] if reasoning else 'unknown'
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute(self, params):
        """增强版 execute - 多引擎智能路由"""
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}

        print(f"🧠 [大脑 v{self.version}] 收到任务: {goal[:100]}")
        
        # 快速数学计算
        import re
        math_match = re.search(r'(\d+)\s*([+\-*/xX])\s*(\d+)', goal)
        if math_match:
            try:
                a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
                if op in ['x', 'X']:
                    op = '*'
                result = eval(f"{a}{op}{b}")
                return self._format_response({"success": True, "result": result}, "math", goal)
            except:
                pass
        
        # 按优先级路由
        priority = self.config.get("priority", [])
        for rule in priority:
            handler_name = rule.get("handler")
            if not self._match_rule(goal, rule):
                continue
            
            print(f"🎯 匹配到规则: {rule.get('name')} -> {handler_name}")
            executor = self.executors.get(handler_name)
            if not executor:
                continue
            
            exec_params = {"goal": goal, "context": params.get("context", {})}
            try:
                if hasattr(executor, 'execute'):
                    result = executor.execute(goal, exec_params)
                elif callable(executor):
                    result = executor(goal, exec_params)
                else:
                    result = {"success": False, "error": f"执行器 {handler_name} 不可调用"}
                
                if result.get("success"):
                    return self._format_response(result, rule.get("name"), goal)
            except Exception as e:
                print(f"⚠️ 执行器 {handler_name} 异常: {e}")
                continue
        
        # 智能兜底
        return self._smart_route(goal)
