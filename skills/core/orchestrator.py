"""工作流编排器 - 组合原子技能"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

class OrchestratorSkill:
    name = "orchestrator"
    description = "编排原子技能完成复杂任务"
    version = "1.0.0"
    category = "core"
    
    # 工作流模板
    WORKFLOWS = {
        "video_creation": [
            {"skill": "script_generator", "output_key": "script"},
            {"skill": "audio_generator", "params": {"text": "{script}"}, "output_key": "audio"},
            {"skill": "video_composer", "params": {"audio_path": "{audio}"}, "output_key": "video"}
        ]
    }
    
    def execute(self, params):
        workflow = params.get("workflow", "video_creation")
        topic = params.get("topic", "")
        
        if workflow not in self.WORKFLOWS:
            return {"success": False, "error": f"未知工作流: {workflow}"}
        
        context = {"topic": topic}
        results = {}
        
        for step in self.WORKFLOWS[workflow]:
            skill_name = step["skill"]
            step_params = step.get("params", {})
            
            # 替换参数中的占位符
            for key, value in step_params.items():
                if isinstance(value, str) and "{" in value:
                    step_params[key] = value.format(**context)
            
            # 执行技能
            result = self._execute_skill(skill_name, step_params)
            
            if not result.get("success"):
                return {"success": False, "error": f"步骤失败: {skill_name}", "step_result": result}
            
            # 保存输出到上下文
            output_key = step.get("output_key", skill_name)
            context[output_key] = result
            results[skill_name] = result
        
        return {
            "success": True,
            "workflow": workflow,
            "results": results,
            "final_output": results.get("video_composer", {}).get("video_path")
        }
    
    def _execute_skill(self, skill_name, params):
        try:
            module = __import__(f"skills.{self._get_skill_path(skill_name)}", fromlist=["skill"])
            return module.skill.execute(params)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_skill_path(self, skill_name):
        paths = {
            "script_generator": "text.script_generator",
            "audio_generator": "audio.audio_generator", 
            "video_composer": "video.video_composer"
        }
        return paths.get(skill_name, skill_name)

skill = OrchestratorSkill()
