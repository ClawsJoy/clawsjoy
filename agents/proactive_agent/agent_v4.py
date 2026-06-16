#!/usr/bin/env python3
"""proactive_agent v4.0 - 智慧化主动服务智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from core.agents.business.business_agent import BusinessAgent


class ProactiveAgentV4(BusinessAgent):
    """智慧化主动服务助手"""
    
    name = "proactive_agent_v4"
    description = "智慧化主动服务助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._reminders = []
        self._suggestions = []
        print(f"💡 {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("remind", "task"): (True, 0.95),
            ("suggest", "action"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 设置提醒
        if any(kw in user_input for kw in ["提醒我", "设置提醒", "闹钟"]):
            return self._set_reminder(user_input)
        
        # 获取建议
        if any(kw in user_input for kw in ["建议", "推荐"]):
            return self._get_suggestions(user_input)
        
        # 查看提醒
        if "我的提醒" in user_input:
            return self._list_reminders()
        
        return self._response(self._get_help())
    
    def _set_reminder(self, user_input: str) -> Dict:
        """设置提醒"""
        # 解析时间
        time_match = re.search(r'(\d+)\s*(分钟|小时|点|分|秒)', user_input)
        if time_match:
            value, unit = int(time_match.group(1)), time_match.group(2)
            if "分钟" in unit:
                delta = timedelta(minutes=value)
            elif "小时" in unit:
                delta = timedelta(hours=value)
            else:
                delta = timedelta(minutes=5)
            remind_time = datetime.now() + delta
        else:
            remind_time = datetime.now() + timedelta(minutes=5)
        
        # 解析内容
        content = re.sub(r'(?:提醒我|设置提醒|闹钟)\s*(?:\d+\s*(?:分钟|小时|点|分|秒))?', '', user_input).strip()
        
        if not content:
            content = "提醒事项"
        
        reminder = {
            "id": len(self._reminders) + 1,
            "content": content,
            "time": remind_time.isoformat(),
            "status": "pending"
        }
        self._reminders.append(reminder)
        
        return self._response(
            f"⏰ 提醒已设置\n\n📝 内容：{content}\n⏰ 时间：{remind_time.strftime('%H:%M:%S')}",
            metadata=reminder
        )
    
   
        
    def _get_help(self) -> str:
        return """💡 **主动服务助手**

支持功能:
- 设置提醒: "提醒我 10分钟后开会"
- 获取建议: "建议 如何提高效率"
- 查看提醒: "我的提醒"

💡 我会学习您的习惯，提供更贴心的服务"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


    def _get_suggestions(self, user_input: str) -> Dict:
        """获取个性化建议"""
        from datetime import datetime
        
        # 获取用户信息
        user_name = self.recall_forever("user_name")
        hour = datetime.now().hour
        
        # 基于时间的建议
        if 5 <= hour < 12:
            time_suggestion = "早上好！新的一天开始了"
            time_advice = "建议先规划今天的任务清单"
        elif 12 <= hour < 14:
            time_suggestion = "中午好"
            time_advice = "建议适当休息，补充能量"
        elif 14 <= hour < 18:
            time_suggestion = "下午好"
            time_advice = "建议专注于重要任务"
        elif 18 <= hour < 22:
            time_suggestion = "晚上好"
            time_advice = "建议回顾今天的工作"
        else:
            time_suggestion = "夜深了"
            time_advice = "建议早点休息，保持充足睡眠"
        
        # 获取用户偏好
        user_prefs = []
        for key in ["颜色", "食物", "电影", "音乐"]:
            value = self.recall_forever(f"pref_{key}")
            if value:
                user_prefs.append(f"{key}: {value}")
        
        # 获取待办数量
        todos = self.recall_forever("todos") or []
        todo_count = len(todos) if isinstance(todos, list) else 0
        
        # 构建建议
        suggestions = []
        
        # 时间建议
        suggestions.append(f"⏰ {time_suggestion}！{time_advice}")
        
        # 待办建议
        if todo_count > 0:
            suggestions.append(f"📋 您还有 {todo_count} 个待办事项待完成")
        else:
            suggestions.append("✅ 当前没有待办事项，可以放松一下")
        
        # 个性化建议（如果有用户偏好）
        if user_prefs:
            suggestions.append(f"🎯 根据您的偏好: {', '.join(user_prefs[:2])}")
        
        # 通用建议（作为补充）
        suggestions.append("💡 提示: 告诉我「我喜欢颜色是蓝色」让我记住你的偏好")
        
        if user_name:
            response = f"{user_name}，{suggestions[0]}\n\n" + "\n".join(suggestions[1:])
        else:
            response = "\n".join(suggestions)
        
        return self._response(response, metadata={"type": "suggestions"})



if __name__ == "__main__":
    agent = ProactiveAgentV4("test")
    print("✅ proactive_agent_v4 测试通过")
