#!/usr/bin/env python3
"""Do Anything - Do Anything 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


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

    def _format_response(self, result, source, original_goal):
        """格式化响应"""
        return {
            "success": result.get("success", True),
            "source": source,
            "original_goal": original_goal[:100],
            "timestamp": datetime.now().isoformat(),
            **{k: v for k, v in result.items() if k not in ['success']}
        }


skill = DoAnythingSkill()
