"""需求分析器 - 拆解复杂需求"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import requests
import json
import re

class RequirementAnalyzerSkill:
    name = "requirement_analyzer"
    description = "分析复杂需求，拆解为子任务"
    version = "1.0.0"
    category = "analysis"

    def execute(self, params):
        requirement = params.get("requirement", "")
        
        if not requirement:
            return {"success": False, "error": "需要需求描述"}
        
        # 判断复杂度
        complexity = self._assess_complexity(requirement)
        
        if complexity == "simple":
            return self._handle_simple(requirement)
        elif complexity == "medium":
            return self._handle_medium(requirement)
        else:
            return self._handle_complex(requirement)
    
    def _assess_complexity(self, text):
        """评估复杂度"""
        words = len(text.split())
        if words < 10:
            return "simple"
        elif words < 30:
            return "medium"
        else:
            return "complex"
    
    def _handle_simple(self, req):
        """简单需求：直接生成"""
        from skills.code_agent_v2 import skill
        return skill.execute({"requirement": req, "auto_register": True})
    
    def _handle_medium(self, req):
        """中等需求：拆解后引导"""
        prompt = f"将以下需求拆解为2-3个简单子任务:\n{req}"
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                            json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                            timeout=60)
        sub_tasks = resp.json()["response"]
        
        return {
            "success": True,
            "complexity": "medium",
            "message": "需求已拆解，请分别处理:",
            "sub_tasks": sub_tasks,
            "suggestion": "请逐个执行子任务"
        }
    
    def _handle_complex(self, req):
        """复杂需求：建议人工介入"""
        return {
            "success": False,
            "complexity": "complex",
            "message": "需求过于复杂，建议人工拆解",
            "suggestion": "请将需求拆分为多个简单需求后分别提交"
        }

skill = RequirementAnalyzerSkill()
