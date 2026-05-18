#!/usr/bin/env python3
"""快速响应 Agent - 减少 LLM 调用，优先规则匹配"""

import re
import logging
from typing import Dict, Any

from core.agent.base import BaseAgent
from lib.skill_registry_v4 import skill_registry
from lib.config_loader import config

logger = logging.getLogger(__name__)


class FastAgent(BaseAgent):
    """快速响应 Agent - 规则优先，LLM 备用"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__("FastAgent")
        self.use_llm = config.get('llm.agent.fallback_enabled', True)
        self._init_rules()
    
    def _init_rules(self):
        """初始化规则"""
        self.rules = [
            {
                "keywords": ["生成", "画", "图片", "图像", "形象", "猫咪", "风景"],
                "skill": "ai-image-gen",
                "extract": lambda x: {"prompt": self._extract_prompt(x)}
            },
            {
                "keywords": ["调度", "定时", "每天", "周期"],
                "skill": "scheduler",
                "extract": lambda x: {"action": "schedule", "task_name": x[:50]}
            },
            {
                "keywords": ["视频", "发布", "上传"],
                "skill": "video_public",
                "extract": lambda x: {"prompt": x}
            }
        ]
    
    def _extract_prompt(self, text: str) -> str:
        """提取提示词"""
        # 移除常见前缀
        prefixes = ["生成", "画", "创建", "做一个", "帮我", "请"]
        result = text
        for p in prefixes:
            if result.startswith(p):
                result = result[len(p):]
                break
        return result.strip() or text
    
    def _match_rule(self, user_input: str) -> Dict:
        """匹配规则"""
        user_lower = user_input.lower()
        
        for rule in self.rules:
            for kw in rule["keywords"]:
                if kw in user_lower:
                    return {
                        "skill": rule["skill"],
                        "params": rule["extract"](user_input),
                        "matched": kw
                    }
        return None
    
    def process(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """处理请求"""
        self.log(f"处理: {user_input[:40]}...")
        
        # 1. 规则匹配（快速）
        match = self._match_rule(user_input)
        
        if match:
            skill_name = match["skill"]
            params = match["params"]
            self.log(f"规则匹配: {match['matched']} -> {skill_name}")
        else:
            # 2. 默认响应
            return {
                "success": False,
                "response": "我能帮你生成图像、调度任务。试试说「生成一张图片」",
                "fallback": True
            }
        
        # 3. 执行技能
        if skill_name not in skill_registry.skills:
            return {
                "success": False,
                "response": f"技能 {skill_name} 暂不可用",
                "error": "skill_not_found"
            }
        
        result = skill_registry.execute_skill(skill_name, params)
        
        # 4. 生成回复
        if result.get('success'):
            if skill_name == "ai-image-gen":
                prompt = params.get('prompt', '')
                response = f"✅ 正在生成图像：{prompt[:50]}..."
            else:
                response = f"✅ 任务已执行"
        else:
            response = f"❌ 执行失败: {result.get('error', '未知错误')}"
        
        return {
            "success": result.get('success', False),
            "skill": skill_name,
            "params": params,
            "result": result,
            "response": response,
            "matched_rule": match.get("matched") if match else None
        }


fast_agent = FastAgent()


if __name__ == "__main__":
    print(f"快速 Agent v{fast_agent.VERSION}")
    
    tests = [
        "生成一个中年男人的形象",
        "画一只猫咪",
        "你好"
    ]
    
    for t in tests:
        print(f"\n{t}")
        result = fast_agent.process(t)
        print(f"  -> {result.get('response')}")
        print(f"  -> 技能: {result.get('skill')}")
