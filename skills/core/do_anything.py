"""大脑调度器 - 使用统一技能加载器"""
import json
import re
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from lib.smart_adapter import smart_adapter
from lib.skill_loader_v3 import skill_loader

class DoAnythingSkill:
    name = "do_anything"
    description = "根据自然语言目标，自主规划并执行任务"
    version = "3.0.0"
    category = "orchestrator"
    
    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}
        
        # 1. 数学计算（直接处理）
        math_result = self._handle_math(goal)
        if math_result.get("success"):
            return math_result
        
        # 2. 抠图任务
        if any(word in goal for word in ['抠图', '去背景', '移除背景']):
            return self._handle_remove_bg(goal)
        
        # 3. 视频制作任务
        if any(word in goal for word in ['视频', '漫剧', '制作']):
            return self._handle_video(goal)
        
        # 4. 其他任务走智能规划
        return self._llm_plan(goal)
    
    def _handle_math(self, goal):
        import re
        text = goal.replace('计算', '').replace('等于', '').strip()
        
        patterns = [
            (r'(\d+)\s*乘\s*(\d+)', lambda a,b: a*b, '×'),
            (r'(\d+)\s*\*\s*(\d+)', lambda a,b: a*b, '×'),
            (r'(\d+)\s*加\s*(\d+)', lambda a,b: a+b, '+'),
            (r'(\d+)\s*\+\s*(\d+)', lambda a,b: a+b, '+'),
            (r'(\d+)\s*减\s*(\d+)', lambda a,b: a-b, '-'),
            (r'(\d+)\s*\-\s*(\d+)', lambda a,b: a-b, '-'),
            (r'(\d+)\s*除\s*(\d+)', lambda a,b: a/b if b!=0 else 0, '÷'),
            (r'(\d+)\s*/\s*(\d+)', lambda a,b: a/b if b!=0 else 0, '÷'),
        ]
        
        for pattern, func, op in patterns:
            match = re.search(pattern, text)
            if match:
                a, b = int(match.group(1)), int(match.group(2))
                result = func(a, b)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                return {
                    "success": True, "goal": goal,
                    "results": [{"skill": "math", "success": True,
                                 "result": {"expression": f"{a} {op} {b}", "result": result}}]
                }
        return {"success": False}
    
    def _handle_remove_bg(self, goal):
        import re
        from pathlib import Path
        
        path_match = re.search(r'([^\s]+\.(jpg|png|jpeg))', goal, re.IGNORECASE)
        if not path_match:
            return {"success": False, "error": "请提供图片路径"}
        
        input_path = path_match.group(1).strip()
        if not Path(input_path).exists():
            return {"success": False, "error": f"图片不存在: {input_path}"}
        
        result = skill_loader.execute('remove_bg', {"input_path": input_path})
        return {"success": result.get("success", False), "goal": goal,
                "results": [{"skill": "remove_bg", "success": result.get("success", False), "result": result}]}
    
    def _handle_video(self, goal):
        import re
        topic_match = re.search(r'[制做作]作?\s*([^，,。]+)', goal)
        topic = topic_match.group(1).strip() if topic_match else goal.replace('视频', '').replace('制作', '').strip()
        
        result = skill_loader.execute('manju_maker', {"topic": topic, "target_duration": 60})
        return {"success": result.get("success", False), "goal": goal,
                "results": [{"skill": "manju_maker", "success": result.get("success", False), "result": result}]}
    
    def _llm_plan(self, goal):
        skills_list = skill_loader.list_skills()[:15]
        prompt = f"目标:{goal}\n可用技能:{skills_list}\n输出JSON:{{\"plan\":[{{\"skill\":\"技能名\",\"params\":{{}}}}]}}"
        
        response = smart_adapter.generate(prompt, auto_select=True)
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                plan = json.loads(match.group())
                if plan and "plan" in plan:
                    return self._execute_plan(plan["plan"], goal)
            except:
                pass
        return {"success": False, "error": "无法生成有效计划"}
    
    def _execute_plan(self, plan, goal):
        results = []
        for step in plan:
            skill_name = step.get("skill")
            result = skill_loader.execute(skill_name, step.get("params", {}))
            results.append({"skill": skill_name, "success": result.get("success", False), "result": result})
        
        from lib.memory_simple import memory
        success_count = len([r for r in results if r.get("success")])
        memory.remember(f"任务|{goal[:50]}|{success_count}/{len(results)}成功", category="workflow_outcome")
        
        return {"success": success_count == len(results), "goal": goal, "results": results}

skill = DoAnythingSkill()
