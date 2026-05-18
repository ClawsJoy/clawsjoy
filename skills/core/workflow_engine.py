from lib.smart_config import smart_config
"""工作流引擎 - 自动组合原子技能完成复杂任务"""
import json
import re
import requests

class WorkflowEngineSkill:
    name = "workflow_engine"
    description = "自动编排原子技能完成复杂任务"
    version = "1.0.0"
    category = "core"
    
    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}
        
        # 1. 分析用户意图
        print(f"🎯 分析目标: {goal}")
        intent = self._analyze_intent(goal)
        
        # 2. 生成执行计划
        print(f"📋 生成计划: {intent['plan']}")
        plan = self._generate_plan(intent)
        
        # 3. 执行计划
        print(f"🚀 执行计划...")
        result = self._execute_plan(plan)
        
        return {
            "success": True,
            "goal": goal,
            "intent": intent,
            "plan": plan,
            "result": result
        }
    
    def _analyze_intent(self, goal):
        """分析用户意图"""
        goal_lower = goal.lower()
        
        # 视频制作意图
        if any(kw in goal_lower for kw in ['视频', '制作', '漫剧']):
            return {
                "type": "video_creation",
                "plan": ["script_generator", "audio_generator", "video_composer"],
                "params": {"topic": self._extract_topic(goal)}
            }
        
        # 内容创作意图
        elif any(kw in goal_lower for kw in ['写', '生成', '创作', '脚本']):
            return {
                "type": "content_creation",
                "plan": ["script_generator"],
                "params": {"topic": self._extract_topic(goal)}
            }
        
        # 数据处理意图
        elif any(kw in goal_lower for kw in ['分析', '统计', '处理']):
            return {
                "type": "data_processing",
                "plan": ["text_processor"],
                "params": {"text": goal}
            }
        
        # 默认：直接调用技能
        else:
            return {
                "type": "direct",
                "plan": [],
                "params": {}
            }
    
    def _extract_topic(self, goal):
        """提取主题"""
        # 简单提取：去掉动词后的内容
        stop_words = ['制作', '生成', '写', '创作', '一个', '帮我']
        topic = goal
        for word in stop_words:
            topic = topic.replace(word, '')
        return topic.strip() or "默认主题"
    
    def _generate_plan(self, intent):
        """生成执行计划"""
        plan = []
        context = {}
        
        for i, skill_name in enumerate(intent["plan"]):
            step = {
                "step": i + 1,
                "skill": skill_name,
                "params": intent["params"].copy(),
                "output_key": f"{skill_name}_output"
            }
            
            # 传递上一步的输出
            if i > 0:
                step["depends_on"] = intent["plan"][i-1]
            
            plan.append(step)
        
        return plan
    
    def _execute_plan(self, plan):
        """执行计划"""
        results = {}
        context = {}
        
        for step in plan:
            skill_name = step["skill"]
            params = step["params"].copy()
            
            # 传递上下文
            if "depends_on" in step:
                prev_output = results.get(step["depends_on"], {})
                if prev_output.get("script"):
                    params["text"] = prev_output["script"]
            
            # 调用技能
            result = self._call_skill(skill_name, params)
            results[skill_name] = result
            context[step["output_key"]] = result
            
            if not result.get("success"):
                return {"error": f"步骤失败: {skill_name}", "results": results}
        
        return {"success": True, "results": results, "context": context}
    
    def _call_skill(self, skill_name, params):
        """调用原子技能"""
        try:
            module = __import__(f"skills.text.{skill_name}", fromlist=["skill"])
            if hasattr(module, 'skill'):
                return module.skill.execute(params)
        except:
            try:
                module = __import__(f"skills.audio.{skill_name}", fromlist=["skill"])
                if hasattr(module, 'skill'):
                    return module.skill.execute(params)
            except:
                try:
                    module = __import__(f"skills.video.{skill_name}", fromlist=["skill"])
                    if hasattr(module, 'skill'):
                        return module.skill.execute(params)
                except:
                    return {"success": False, "error": f"技能 {skill_name} 不存在"}
        return {"success": False, "error": f"技能 {skill_name} 调用失败"}

skill = WorkflowEngineSkill()
