#!/usr/bin/env python3
"""ChatAgent v3.0 - 通用对话智能体"""

import random
import re
from datetime import datetime
from typing import Dict, Optional

from core.agents.business.base_business_agent import BusinessAgent
from core.lib.smart_adapter import smart_adapter


class ChatAgent(BusinessAgent):
    """
    通用对话智能体

    能力:
    - 日常对话
    - 原子技能（天气、计算、时间、随机数）
    - 话本匹配
    - 名字识别
    - LLM 兜底
    """

    name = "chat_agent"
    description = "通用对话助手"
    version = "3.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.user_name = None
        print(f"💬 ChatAgent v3.0 已上线")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        """核心业务逻辑"""

        # 1. 原子技能（快速路径）
        atomic_result = self._check_atomic_skill(user_input)
        if atomic_result:
            self.record_interaction(user_input, atomic_result)
            return {
                "success": True,
                "response": atomic_result,
                "skill_type": "atomic",
            }

        # 2. 话本匹配
        intent = self._match_intent(user_input)
        if intent:
            template = self._get_template(intent)
            if template:
                self.record_interaction(user_input, template)
                return {
                    "success": True,
                    "response": template,
                    "intent": intent,
                }

        # 3. 名字提取
        name = self._extract_name(user_input)
        if name:
            self.user_name = name
            self.remember_forever("user_name", name)
            response = f"你好，{name}！很高兴认识你！"
            self.record_interaction(user_input, response)
            return {
                "success": True,
                "response": response,
                "user_name": name,
            }

        # 4. LLM 兜底
        response = self._llm_chat(user_input)
        self.record_interaction(user_input, response)

        return {
            "success": True,
            "response": response,
            "source": "llm",
        }

    def _check_atomic_skill(self, user_input: str) -> Optional[str]:
        """原子技能"""
        u = user_input.lower()

        # 天气
        m = re.search(r"([\u4e00-\u9fa5]{2,3})天气", user_input)
        if m:
            city = m.group(1)
            weathers = ["晴 ☀️", "多云 ⛅", "阴 ☁️", "小雨 🌧️", "雪 ❄️"]
            return f"📍 {city}天气：{random.choice(weathers)}"

        # 方言翻译
        m = re.search(r"用(.{2,3})说(.+)", user_input)
        if m:
            return f"🗣️ {m.group(1)}：{m.group(2)}"

        # 数学计算
        m = re.search(r"(\d+)\s*([\+\-\*/])\s*(\d+)", user_input)
        if m:
            try:
                a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
                result = eval(f"{a}{op}{b}")
                return f"{a}{op}{b} = {result}"
            except:
                pass

        # 时间
        if any(w in u for w in ["时间", "几点", "日期"]):
            now = datetime.now()
            return f"📅 {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

        # 随机数
        if "随机" in u:
            return f"🎲 随机数：{random.randint(1, 100)}"

        return None

    def _match_intent(self, user_input: str) -> Optional[str]:
        """话本匹配"""
        if "你是谁" in user_input or "你叫什么" in user_input:
            return "identity"
        if "ClawsJoy" in user_input or "clawsjoy" in user_input.lower():
            return "about"
        if "你好" in user_input or "您好" in user_input:
            return "greeting"
        if "谢谢" in user_input:
            return "thanks"
        if "再见" in user_input:
            return "farewell"
        if "能做什么" in user_input or "功能" in user_input:
            return "capabilities"
        return None

    def _get_template(self, intent: str) -> Optional[str]:
        """获取话本模板"""
        templates = {
            "identity": "我是 ClawsJoy 助手，您的智能助手！🎉\n\n我可以帮您查天气、翻译方言、计算、回答问题。",
            "about": "ClawsJoy 是一个智能体操作系统！🎯\n\n可以帮您完成各种任务，支持多 Agent 协作。",
            "greeting": f"您好{'，' + self.user_name if self.user_name else ''}！我是 ClawsJoy 助手，很高兴为您服务！✨\n\n有什么我可以帮您的吗？",
            "thanks": "不客气！很高兴能帮到您！😊",
            "farewell": "再见！欢迎随时回来！👋",
            "capabilities": "我可以帮您：\n• 查天气\n• 翻译方言\n• 数学计算\n• 回答问题\n• 生成代码\n• 分析数据",
        }
        return templates.get(intent)

    def _extract_name(self, user_input: str) -> Optional[str]:
        """提取用户名字"""
        patterns = [
            r"我叫[\s]*([^\s，。！？]{2,4})",
            r"我是[\s]*([^\s，。！？]{2,4})",
            r"名字[叫是][\s]*([^\s，。！？]{2,4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1)
        return None

    def _llm_chat(self, user_input: str) -> str:
        """LLM 聊天"""
        prompt = f"用户说：{user_input}\n请友好、简洁地回复。"
        try:
            response = smart_adapter.generate(prompt, auto_select=True)
            return response.strip()
        except Exception as e:
            return f"收到您的消息：{user_input[:50]}..."

    def record_interaction(self, user_input: str, response: str):
        """记录交互"""
        self.remember_forever(
            f"last_interaction",
            {
                "input": user_input[:100],
                "response": response[:100],
                "timestamp": datetime.now().isoformat(),
            },
        )


chat_agent = ChatAgent()
