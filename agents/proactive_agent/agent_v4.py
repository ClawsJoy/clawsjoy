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
        
        return self._response(self._smart_fallback(user_input))
    
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
    
   
        
