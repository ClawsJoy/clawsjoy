#!/usr/bin/env python3
"""配置驱动的 LLM Agent - 无硬编码"""

import json
import requests
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from core.agent.base import BaseAgent
from lib.skill_registry_v4 import skill_registry
from lib.config_loader import config

logger = logging.getLogger(__name__)


class ConfigLLMAgent(BaseAgent):
    """配置驱动的 LLM 代理 - 所有参数从配置读取"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__("ConfigLLMAgent")
        
        # 从配置读取所有参数
        self.ollama_host = config.get('llm.ollama.host', '127.0.0.1')
        self.ollama_port = config.get('llm.ollama.port', 11434)
        self.ollama_timeout = config.get('llm.ollama.timeout', 60)
        self.default_model = config.get('llm.models.default', 'qwen2.5:7b')
        self.max_history = config.get('llm.agent.max_history', 10)
        self.fallback_enabled = config.get('llm.agent.fallback_enabled', True)
        
        # 构建 Ollama URL
        self.ollama_url = f"http://{self.ollama_host}:{self.ollama_port}"
        
        self._load_skills()
        self.log(f"初始化完成: Ollama={self.ollama_url}, 模型={self.default_model}")
    
    def _load_skills(self):
        """加载技能描述"""
        self.skills_desc = []
        for skill_name in skill_registry.skills.keys():
            skill = skill_registry.get_skill(skill_name)
            if skill:
                self.skills_desc.append({
                    "name": skill_name,
                    "description": skill.description[:200]
                })
        self.log(f"加载了 {len(self.skills_desc)} 个技能")
    
    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM - 配置驱动"""
        model = model or self.default_model
        
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=self.ollama_timeout
            )
            if resp.status_code == 200:
                return resp.json().get('response', '')
            else:
                self.log(f"LLM 调用失败: {resp.status_code}")
                return ""
        except Exception as e:
            self.log(f"LLM 调用异常: {e}")
            return ""
    
    def _build_decision_prompt(self, user_input: str) -> str:
        """构建决策提示词"""
        skills_text = "\n".join([
            f"- {s['name']}: {s['description'][:80]}"
            for s in self.skills_desc
        ])
        
        return f"""你是一个智能助手，可以调用以下技能:

{skills_text}

用户说: "{user_input}"

请分析并返回 JSON:
{{
    "skill": "技能名称",
    "params": {{"参数": "值"}},
    "reasoning": "理由"
}}

只返回 JSON。"""
    
    def _extract_params(self, user_input: str, skill_name: str) -> Dict:
        """提取参数"""
        params = {}
        
        if skill_name == "ai-image-gen":
            # 提取 prompt
            prompt = user_input
            for prefix in ["生成", "画", "创建", "做一个"]:
                if user_input.startswith(prefix):
                    prompt = user_input[len(prefix):]
                    break
            params["prompt"] = prompt.strip()
        
        return params
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        self.log(f"处理: {user_input[:50]}...")
        
        # 1. LLM 决策
        decision_prompt = self._build_decision_prompt(user_input)
        llm_response = self._call_llm(decision_prompt)
        
        skill_name = None
        params = {}
        
        if llm_response:
            try:
                # 提取 JSON
                import re
                json_match = re.search(r'\{[^}]+\}', llm_response)
                if json_match:
                    decision = json.loads(json_match.group())
                    skill_name = decision.get('skill')
                    params = decision.get('params', {})
            except:
                pass
        
        # 2. 备用规则
        if not skill_name:
            if any(kw in user_input for kw in ['生成', '画', '图片', '图像']):
                skill_name = "ai-image-gen"
                params = self._extract_params(user_input, skill_name)
            else:
                return {
                    "success": False,
                    "response": "请明确您的需求",
                    "fallback": True
                }
        
        # 3. 执行技能
        if skill_name not in skill_registry.skills:
            return {
                "success": False,
                "response": f"技能 {skill_name} 不可用",
                "error": "skill_not_found"
            }
        
        result = skill_registry.execute_skill(skill_name, params)
        
        # 4. 生成回复
        if result.get('success'):
            response = f"✅ 已执行 {skill_name}"
            if skill_name == "ai-image-gen":
                response = f"✅ 正在生成图像: {params.get('prompt', '')[:50]}..."
        else:
            response = f"❌ 执行失败: {result.get('error', '未知错误')}"
        
        return {
            "success": result.get('success', False),
            "skill": skill_name,
            "params": params,
            "result": result,
            "response": response,
            "llm_used": bool(llm_response)
        }


config_agent = ConfigLLMAgent()


if __name__ == "__main__":
    print(f"配置驱动 LLM Agent v{config_agent.VERSION}")
    print(f"Ollama: {config_agent.ollama_url}")
    print(f"模型: {config_agent.default_model}")
    
    result = config_agent.process("生成一个中年男人的形象")
    print(f"\n结果: {result.get('response')}")
    print(f"技能: {result.get('skill')}")
    print(f"参数: {result.get('params')}")
