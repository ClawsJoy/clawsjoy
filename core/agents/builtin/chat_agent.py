#!/usr/bin/env python3
"""Chat Agent - Chat Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from typing import Dict, Optional
import random
import re
from datetime import datetime
from core.agents.base.smart_agent import SmartAgent


class ChatAgent(SmartAgent):
    name = "chat_agent"
    description = "通用对话助手"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"💬 ChatAgent 已上线")

    def _check_location(self, user_input: str):
        """位置识别"""
        locations = {
            "宁波镇海": "宁波市镇海区，位于浙江东北部，东海之滨",
            "镇海": "宁波市镇海区，有招宝山、九龙湖等景点",
            "宁波": "浙江省宁波市，港口城市，有天一阁、老外滩",
            "北京": "中国首都，政治文化中心",
            "上海": "直辖市，经济金融中心",
        }
        for loc, desc in locations.items():
            if loc in user_input:
                return desc
        return None

    def _check_atomic_skill(self, user_input: str):
        """原子技能"""
        u = user_input.lower()
        
        # 天气
        m = re.search(r"([\u4e00-\u9fa5]{2,3})天气", user_input)
        if m:
            city = m.group(1)
            weathers = ["晴 ☀️", "多云 ⛅", "阴 ☁️", "小雨 🌧️"]
            return f"📍 {city}天气：{random.choice(weathers)}"
        
        # 方言
        m = re.search(r"用(.{2,3})说(.+)", user_input)
        if m:
            return f"🗣️ {m.group(1)}：{m.group(2)}"
        
        # 计算
        m = re.search(r"(\d+)\s*[\+\-\*/]\s*(\d+)", user_input)
        if m:
            try:
                a, b = int(m.group(1)), int(m.group(2))
                op = re.search(r"[\+\-\*/]", user_input).group()
                return f"{a}{op}{b} = {eval(f'{a}{op}{b}')}"
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

    def _match_intent(self, user_input: str):
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

    def _get_template(self, intent: str):
        """获取话本模板"""
        templates = {
            "identity": "我是 ClawsJoy 助手，您的智能语音助手！🎉\n\n我可以帮您查天气、翻译方言、计算、回答各种问题。",
            "about": "ClawsJoy 是一个智能体操作系统！🎯\n\n可以帮您完成各种任务，支持语音交互、知识学习。",
            "greeting": "您好！我是 ClawsJoy 助手，很高兴为您服务！✨\n\n有什么我可以帮您的吗？",
            "thanks": "不客气！很高兴能帮到您！😊",
            "farewell": "再见！欢迎随时回来！👋",
            "capabilities": "我可以帮您：\n• 查天气：「北京天气」\n• 方言：「用粤语说你好」\n• 计算：「1+2」\n• 时间：「现在几点」\n• 回答问题\n• 学习知识",
        }
        return templates.get(intent)

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户输入"""
        try:
            # 位置识别
            location = self._check_location(user_input)
            if location:
                return {
                    "success": True,
                    "response": f"📍 {location}",
                    "agent": self.name,
                    "user_id": self.user_id
                }
            
            # 原子技能
            atomic = self._check_atomic_skill(user_input)
            if atomic:
                return {
                    "success": True,
                    "response": atomic,
                    "agent": self.name,
                    "user_id": self.user_id
                }
            
            # 话本
            intent = self._match_intent(user_input)
            if intent:
                tmpl = self._get_template(intent)
                if tmpl:
                    return {
                        "success": True,
                        "response": tmpl,
                        "agent": self.name,
                        "user_id": self.user_id
                    }
            
            # 兜底
            return {
                "success": True,
                "response": f"🤔 您说的「{user_input[:30]}」我不太理解。试试「北京天气」「用粤语说你好」「1+2」",
                "agent": self.name,
                "user_id": self.user_id
            }
        except Exception as e:
            return {
                "success": True,
                "response": f"处理出错: {e}",
                "agent": self.name,
                "user_id": self.user_id
            }
