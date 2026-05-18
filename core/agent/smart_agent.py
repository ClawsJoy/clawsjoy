#!/usr/bin/env python3
"""真正的智能体 - 保留 LLM 分析层"""

import json
import requests
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.agent.base import BaseAgent
from lib.skill_registry_v4 import skill_registry
from lib.config_loader import config
from lib.memory_simple import memory

logger = logging.getLogger(__name__)


class SmartAgent(BaseAgent):
    """真正的智能体 - 有 LLM 分析层，能学习、能升级"""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        super().__init__("SmartAgent")
        
        # 从配置读取
        self.ollama_host = config.get('llm.ollama.host', '127.0.0.1')
        self.ollama_port = config.get('llm.ollama.port', 11434)
        self.model = config.get('llm.models.default', 'qwen2.5:3b')
        self.fallback_model = config.get('llm.models.fallback', 'qwen2.5:7b')
        self.timeout = config.get('llm.ollama.timeout', 15)
        
        self.ollama_url = f"http://{self.ollama_host}:{self.ollama_port}"
        self.learn_from_feedback = config.get('llm.agent.learn_from_feedback', True)
        
        self._load_skills()
        self._load_memory()
    
    def _load_skills(self):
        """加载技能描述"""
        self.skills_desc = []
        for name, skill in skill_registry.skills.items():
            self.skills_desc.append({
                "name": name,
                "description": skill.description[:150],
                "params": self._get_skill_params_hint(name)
            })
        logger.info(f"加载 {len(self.skills_desc)} 个技能")
    
    def _get_skill_params_hint(self, skill_name: str) -> str:
        """获取技能参数提示"""
        hints = {
            "ai-image-gen": "需要 prompt 参数（图像描述）",
            "scheduler": "需要 action 和 task_name",
            "video_public": "需要 video_path"
        }
        return hints.get(skill_name, "无特殊参数")
    
    def _load_memory(self):
        """加载记忆"""
        try:
            self.conversations = memory.recall_all(category="conversation")[-20:]
        except:
            self.conversations = []
    
    def _save_to_memory(self, user_input: str, response: str):
        """保存到记忆"""
        try:
            memory.remember(
                f"用户: {user_input}\n助手: {response[:200]}",
                category="conversation"
            )
        except:
            pass
    
    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM - 带重试"""
        model = model or self.model
        
        for attempt in range(2):
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    return resp.json().get('response', '')
            except requests.Timeout:
                logger.warning(f"LLM 超时 (尝试 {attempt + 1}/2)")
                if attempt == 0 and self.fallback_model:
                    model = self.fallback_model
                    continue
            except Exception as e:
                logger.error(f"LLM 错误: {e}")
        
        return ""
    
    def _build_decision_prompt(self, user_input: str) -> str:
        """构建决策提示词 - 完整版"""
        skills_text = "\n".join([
            f"- {s['name']}: {s['description'][:100]}. 参数: {s['params']}"
            for s in self.skills_desc
        ])
        
        return f"""你是一个智能助手，可以调用以下技能来帮助用户。

可用技能:
{skills_text}

用户说: "{user_input}"

请分析并返回 JSON（只返回 JSON）:
{{
    "intent": "用户想要做什么",
    "skill": "选择的技能名称",
    "params": {{"参数名": "从用户输入提取的参数值"}},
    "reasoning": "为什么选择这个技能"
}}

示例:
用户说"生成一个中年男人的形象" → {{"skill": "ai-image-gen", "params": {{"prompt": "中年男人的形象"}}}}
用户说"明天早上9点提醒我开会" → {{"skill": "scheduler", "params": {{"action": "schedule", "task_name": "开会", "time": "09:00"}}}}
"""
    
    def _build_summary_prompt(self, user_input: str, skill: str, result: Dict) -> str:
        """构建总结提示词"""
        return f"""用户: {user_input}
执行了技能: {skill}
结果: {"成功" if result.get('success') else "失败"} {result.get('result', {}).get('message', '')}

请用自然语言回复用户，要友好热情。"""
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求 - 完整 LLM 分析"""
        logger.info(f"处理: {user_input[:50]}...")
        
        # 1. LLM 分析意图（核心！不能去掉）
        logger.info("LLM 分析意图...")
        decision_prompt = self._build_decision_prompt(user_input)
        llm_response = self._call_llm(decision_prompt)
        
        if not llm_response:
            # LLM 不可用时的降级处理
            return self._fallback_process(user_input)
        
        # 解析 LLM 响应
        try:
            json_match = re.search(r'\{[^{}]*\}', llm_response)
            if json_match:
                decision = json.loads(json_match.group())
                skill_name = decision.get('skill')
                params = decision.get('params', {})
                reasoning = decision.get('reasoning', '')
                logger.info(f"决策: {reasoning}")
                logger.info(f"技能: {skill_name}, 参数: {params}")
        except Exception as e:
            logger.error(f"解析失败: {e}")
            return self._fallback_process(user_input)
        
        # 2. 执行技能
        if not skill_name or skill_name not in skill_registry.skills:
            return {
                "success": False,
                "response": f"抱歉，我不懂怎么处理「{user_input[:50]}」",
                "available_skills": list(skill_registry.skills.keys())[:5],
                "fallback": True
            }
        
        logger.info(f"执行技能: {skill_name}")
        result = skill_registry.execute_skill(skill_name, params)
        
        # 3. LLM 总结结果
        logger.info("LLM 生成回复...")
        summary_prompt = self._build_summary_prompt(user_input, skill_name, result)
        summary = self._call_llm(summary_prompt, self.fallback_model)
        
        response = summary if summary else self._format_result(result, skill_name, params)
        
        # 4. 学习与记忆
        self._save_to_memory(user_input, response)
        
        # 5. 记录执行日志用于学习
        self._record_outcome(skill_name, result.get('success', False))
        
        return {
            "success": result.get('success', False),
            "skill": skill_name,
            "params": params,
            "result": result,
            "response": response,
            "reasoning": reasoning,
            "llm_analyzed": True
        }
    
    def _record_outcome(self, skill: str, success: bool):
        """记录执行结果，用于学习"""
        try:
            memory.remember(
                f"技能:{skill}|成功:{success}|时间:{datetime.now().isoformat()}",
                category="skill_performance"
            )
        except:
            pass
    
    def _fallback_process(self, user_input: str) -> Dict[str, Any]:
        """降级处理 - 当 LLM 不可用时"""
        logger.warning("LLM 不可用，使用降级模式")
        
        # 简单关键词匹配
        if any(kw in user_input for kw in ['生成', '画', '图片']):
            skill_name = "ai-image-gen"
            params = {"prompt": user_input}
            result = skill_registry.execute_skill(skill_name, params)
            return {
                "success": result.get('success', False),
                "skill": skill_name,
                "response": self._format_result(result, skill_name, params),
                "fallback": True,
                "llm_analyzed": False
            }
        
        return {
            "success": False,
            "response": "我能帮你生成图像、调度任务。试试说「生成一张图片」",
            "fallback": True,
            "llm_analyzed": False
        }
    
    def _format_result(self, result: Dict, skill: str, params: Dict) -> str:
        """格式化结果"""
        if result.get('success'):
            if skill == "ai-image-gen":
                return f"✅ 正在生成图像：{params.get('prompt', '')[:50]}..."
            return f"✅ {skill} 执行成功"
        else:
            return f"❌ 执行失败: {result.get('error', '未知错误')}"
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": self.VERSION,
            "model": self.model,
            "ollama": self.ollama_url,
            "skills": len(self.skills_desc),
            "learning_enabled": self.learn_from_feedback
        }


smart_agent = SmartAgent()


if __name__ == "__main__":
    print(f"智能体 v{smart_agent.VERSION}")
    print(f"模型: {smart_agent.model}")
    print(f"Ollama: {smart_agent.ollama_url}")
    
    result = smart_agent.process("生成一个中年男人的形象")
    print(f"\n结果: {result.get('response')}")
    print(f"LLM 分析: {result.get('llm_analyzed')}")

# 集成学习模块
from core.agent.learner import agent_learner

# 在 process 方法中添加学习记录
# （需要在 process 方法末尾添加）
