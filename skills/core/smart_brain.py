"""智能大脑 - 优先使用工作流，失败则动态组合原子技能"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

from lib.skill_schema import skill_registry, SkillType
from lib.skill_loader_v3 import skill_loader
import json
import requests

class SmartBrainSkill:
    name = "smart_brain"
    description = "智能大脑：优先使用工作流，失败则动态组合原子技能"
    version = "1.0.0"
    category = "core"
    
    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}
        
        print(f"🧠 智能大脑分析: {goal}")
        
        # 第一步：尝试匹配已有工作流
        workflow = skill_registry.get_best_workflow(goal)
        
        if workflow:
            print(f"📋 匹配到工作流: {workflow}")
            result = self._execute_workflow(workflow, {"topic": self._extract_topic(goal)})
            
            if result.get("success"):
                skill_registry.update_success_rate(workflow, True)
                return {
                    "success": True,
                    "method": "workflow",
                    "workflow": workflow,
                    "result": result
                }
            else:
                print(f"⚠️ 工作流执行失败: {result.get('error')}")
                skill_registry.update_success_rate(workflow, False)
        
        # 第二步：失败后动态组合原子技能
        print("🔧 尝试动态组合原子技能...")
        atomic_result = self._compose_atomic_skills(goal)
        
        return {
            "success": atomic_result.get("success", False),
            "method": "atomic_composition",
            "result": atomic_result
        }
    
    def _execute_workflow(self, workflow_name: str, context: dict) -> dict:
        """执行已注册的工作流"""
        manifest = skill_registry.get(workflow_name)
        if not manifest:
            return {"success": False, "error": f"工作流不存在: {workflow_name}"}
        
        results = {}
        for step in manifest.steps:
            skill_name = step["skill"]
            params = step.get("params", {}).copy()
            
            # 替换参数中的占位符
            for key, value in params.items():
                if isinstance(value, str) and "{" in value:
                    params[key] = value.format(**context, **results)
            
            # 调用技能
            result = skill_loader.execute(skill_name, params)
            results[step.get("output_key", skill_name)] = result
            
            if not result.get("success"):
                return {"success": False, "error": f"步骤失败: {skill_name}", "step_result": result}
        
        return {"success": True, "results": results}
    
    def _compose_atomic_skills(self, goal: str) -> dict:
        """动态组合原子技能"""
        intent = self._analyze_intent(goal)
        
        if intent["type"] == "video":
            # 视频制作组合
            script_result = skill_loader.execute("script_generator", {"topic": intent["topic"]})
            if not script_result.get("success"):
                return {"success": False, "error": "脚本生成失败"}
            
            audio_result = skill_loader.execute("audio_generator", {"text": script_result.get("script", "")})
            video_result = skill_loader.execute("video_composer", {"duration": 30})
            
            return {
                "success": True,
                "script": script_result.get("script"),
                "audio": audio_result.get("audio_path"),
                "video": video_result.get("video_path")
            }
        
        elif intent["type"] == "script":
            result = skill_loader.execute("script_generator", {"topic": intent["topic"]})
            return {"success": result.get("success", False), "script": result.get("script")}
        
        else:
            return {"success": False, "error": "无法识别目标类型"}
    
    def _analyze_intent(self, goal: str) -> dict:
        """分析用户意图"""
        goal_lower = goal.lower()
        if any(kw in goal_lower for kw in ['视频', '制作', '漫剧']):
            return {"type": "video", "topic": self._extract_topic(goal)}
        elif any(kw in goal_lower for kw in ['脚本', '写', '生成']):
            return {"type": "script", "topic": self._extract_topic(goal)}
        else:
            return {"type": "unknown", "topic": goal}
    
    def _extract_topic(self, goal: str) -> str:
        """提取主题"""
        stop_words = ['制作', '生成', '写', '创作', '一个', '帮我', '视频', '脚本']
        topic = goal
        for word in stop_words:
            topic = topic.replace(word, '')
        return topic.strip() or "默认主题"

skill = SmartBrainSkill()
