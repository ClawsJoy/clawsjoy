#!/usr/bin/env python3
"""LLM Agent - 增强参数提取版"""

import json
import requests
import logging
import re
from typing import Dict, Any, Optional

from core.agent.base import BaseAgent
from lib.skill_registry_v4 import skill_registry
from lib.config_loader import config

logger = logging.getLogger(__name__)


class LLMAgent(BaseAgent):
    """基于 LLM 的智能代理 - 增强版"""
    
    def __init__(self):
        super().__init__("LLMAgent")
        self.ollama_url = config.get('llm.endpoint', 'http://127.0.0.1:11434')
        self.model = config.get('llm.default_model', 'qwen2.5:7b')
        self._load_skills()
    
    def _load_skills(self):
        """加载技能描述（包含参数说明）"""
        self.skills_desc = []
        for skill_name in skill_registry.skills.keys():
            skill = skill_registry.get_skill(skill_name)
            if skill:
                # 添加参数说明
                param_hint = ""
                if skill_name == "ai-image-gen":
                    param_hint = "需要 prompt 参数（图像描述）"
                elif skill_name == "scheduler":
                    param_hint = "需要 action 参数（schedule/list/cancel）和 task_name"
                
                self.skills_desc.append({
                    "name": skill_name,
                    "description": skill.description[:200],
                    "params": param_hint
                })
        self.log(f"加载了 {len(self.skills_desc)} 个技能")
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get('response', '')
            return ""
        except Exception as e:
            self.log(f"LLM 调用异常: {e}")
            return ""
    
    def _build_decision_prompt(self, user_input: str) -> str:
        """构建决策提示词（包含参数要求）"""
        skills_text = "\n".join([
            f"- {s['name']}: {s['description'][:100]}. 参数: {s['params']}"
            for s in self.skills_desc
        ])
        
        return f"""你是一个智能代理，需要理解用户需求并决定调用哪个技能。

可用技能:
{skills_text}

重要: 必须从用户输入中提取参数值。

用户请求: {user_input}

请返回 JSON 格式（只返回 JSON，不要有其他内容）:
{{
    "intent": "用户意图简述",
    "skill": "技能名称",
    "params": {{"参数名": "从用户输入提取的参数值"}},
    "reasoning": "选择理由"
}}

示例:
用户说"生成一个中年男人的形象" -> {{"skill": "ai-image-gen", "params": {{"prompt": "中年男人的形象"}}}}
用户说"生成一只猫咪" -> {{"skill": "ai-image-gen", "params": {{"prompt": "一只猫咪"}}}}
"""
    
    def _build_summary_prompt(self, user_input: str, skill: str, result: Dict) -> str:
        """构建总结提示词"""
        return f"""用户请求: {user_input}
调用了技能: {skill}
执行结果: {json.dumps(result, ensure_ascii=False)[:500]}

请用自然语言回复用户，说明执行结果。回复要简洁友好。"""
    
    def _extract_prompt_from_input(self, user_input: str) -> str:
        """备用：从用户输入提取 prompt"""
        # 移除常见前缀
        prefixes = ["生成", "画", "创建", "做一个", "帮我生成"]
        text = user_input
        for p in prefixes:
            if text.startswith(p):
                text = text[len(p):]
        return text.strip()
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        self.log(f"处理请求: {user_input[:50]}...")
        
        # 1. LLM 决策
        self.log("LLM 分析中...")
        decision_prompt = self._build_decision_prompt(user_input)
        llm_response = self._call_llm(decision_prompt)
        
        if not llm_response:
            return self._fallback_process(user_input)
        
        try:
            # 提取 JSON
            json_str = llm_response
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            elif '```' in json_str:
                json_str = json_str.split('```')[1].split('```')[0]
            
            decision = json.loads(json_str.strip())
            skill_name = decision.get('skill', '')
            params = decision.get('params', {})
            reasoning = decision.get('reasoning', '')
            
            # 如果是 ai-image-gen 但没有 prompt，自动提取
            if skill_name == "ai-image-gen" and not params.get('prompt'):
                params['prompt'] = self._extract_prompt_from_input(user_input)
                self.log(f"自动提取 prompt: {params['prompt'][:50]}...")
            
            self.log(f"决策: {reasoning}")
            self.log(f"技能: {skill_name}, 参数: {params}")
            
        except Exception as e:
            self.log(f"决策解析失败: {e}, 使用备用")
            return self._fallback_process(user_input)
        
        # 2. 执行技能
        if not skill_name or skill_name not in skill_registry.skills:
            return {
                "success": False,
                "error": f"技能 '{skill_name}' 不存在",
                "available_skills": list(skill_registry.skills.keys())[:10],
                "response": f"抱歉，技能 '{skill_name}' 不可用。可用技能: {', '.join(list(skill_registry.skills.keys())[:5])}"
            }
        
        self.log(f"执行技能: {skill_name}")
        result = skill_registry.execute_skill(skill_name, params)
        
        # 3. LLM 总结
        self.log("生成回复...")
        summary_prompt = self._build_summary_prompt(user_input, skill_name, result)
        summary = self._call_llm(summary_prompt)
        
        return {
            "success": result.get('success', False),
            "skill": skill_name,
            "params": params,
            "result": result,
            "response": summary if summary else self._format_result(result),
            "decision": decision
        }
    
    def _fallback_process(self, user_input: str) -> Dict[str, Any]:
        """备用规则匹配"""
        self.log("使用规则匹配（LLM 不可用）")
        
        # 提取 prompt
        prompt = self._extract_prompt_from_input(user_input)
        
        if any(kw in user_input for kw in ['生成', '图片', '图像', '画']):
            skill_name = "ai-image-gen"
            params = {"prompt": prompt}
        else:
            return {
                "success": False,
                "error": "无法理解用户意图",
                "response": "请明确描述您的需求，例如：生成一张图片"
            }
        
        result = skill_registry.execute_skill(skill_name, params)
        
        return {
            "success": result.get('success', False),
            "skill": skill_name,
            "params": params,
            "result": result,
            "response": self._format_result(result),
            "fallback": True
        }
    
    def _format_result(self, result: Dict) -> str:
        """格式化结果"""
        if result.get('success'):
            msg = result.get('result', {}).get('message', '任务执行成功')
            return f"✅ {msg}"
        else:
            return f"❌ 执行失败: {result.get('error', '未知错误')}"


llm_agent = LLMAgent()


if __name__ == "__main__":
    print("LLM Agent 测试")
    print("=" * 40)
    
    test_inputs = [
        "生成一个中年男人的形象",
        "画一只猫咪",
        "帮我生成一张风景图"
    ]
    
    for inp in test_inputs:
        print(f"\n👤 {inp}")
        result = llm_agent.process(inp)
        print(f"🤖 {result.get('response', '')[:100]}")
        print(f"   [技能: {result.get('skill')}, 参数: {result.get('params')}]")
