#!/usr/bin/env python3
"""Self Learning Brain - Self Learning Brain 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""自学习大脑 - 从经验中学习"""
import json
import re
import requests
from src.config.settings import settings
from lib.memory_simple import memory

class SelfLearningBrain:
    """自学习大脑 - 从成功/失败经验中学习"""
    
    def __init__(self):
        self.ollama_url = settings.get_ollama_url()
        self.default_model = settings.DEFAULT_MODEL
    
    def process(self, user_input):
        # 1. 先查记忆：是否有类似成功案例
        similar = self._find_similar_case(user_input)
        if similar:
            print(f"📚 从记忆中复用: {similar['pattern']}")
            return self._execute_plan(similar['plan'])
        
        # 2. 没有记忆，用 LLM 推理
        plan = self._reason(user_input)
        
        # 3. 执行计划
        result = self._execute_plan(plan)
        
        # 4. 学习：记录成功或失败
        self._learn(user_input, plan, result)
        
        return result
    
    def _find_similar_case(self, input_text):
        """从记忆中查找相似案例"""
        cases = memory.recall_all(category='success_patterns')
        for case in cases[-20:]:  # 最近20条
            try:
                data = json.loads(case)
                if data.get('pattern') in input_text:
                    return data
            except:
                pass
        return None
    
    def _reason(self, input_text):
        """LLM 推理执行计划"""
        # 获取可用技能列表
        from src.api.gateway import _skills
        skills_desc = "\n".join([f"- {name}: {getattr(skill, 'description', name)}" 
                                  for name, skill in list(_skills.items())[:20]])
        
        prompt = f"""用户需求: {input_text}

可用技能:
{skills_desc}

请输出执行计划 JSON:
{{"steps": [{{"skill": "技能名", "params": {{"参数": "值"}}}}]}}

只输出 JSON。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": self.default_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            }, timeout=60)
            response = resp.json().get("response", "")
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            print(f"推理失败: {e}")
        
        return {"steps": []}
    
    def _execute_plan(self, plan):
        """执行计划"""
        from src.api.gateway import _skills, _legacy_skills, _workflows
        
        results = []
        for step in plan.get("steps", []):
            skill_name = step.get("skill")
            params = step.get("params", {})
            
            if skill_name in _skills:
                result = _skills[skill_name].execute(params)
                results.append({"skill": skill_name, "result": result})
            elif skill_name in _workflows:
                result = _workflows[skill_name].execute(params)
                results.append({"skill": skill_name, "result": result})
            elif skill_name in _legacy_skills:
                result = _legacy_skills[skill_name]['loader'].execute(skill_name, params)
                results.append({"skill": skill_name, "result": result})
            else:
                results.append({"skill": skill_name, "result": {"success": False, "error": "技能不存在"}})
        
        success = all(r.get("result", {}).get("success", False) for r in results)
        return {"success": success, "results": results, "plan": plan}
    
    def _learn(self, input_text, plan, result):
        """学习：记录成功经验"""
        if result.get("success"):
            # 记录成功模式
            pattern = self._extract_pattern(input_text)
            memory.remember(
                json.dumps({
                    "pattern": pattern,
                    "plan": plan,
                    "success": True,
                    "count": 1
                }),
                category='success_patterns'
            )
            print(f"🧠 学习了新模式: {pattern}")
    
    def _extract_pattern(self, text):
        """提取模式（简化）"""
        # 去除具体词汇，保留结构
        words = text.split()
        if len(words) > 3:
            return f"{words[0]}...{words[-1]}"
        return text

brain = SelfLearningBrain()
