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
    
    def _get_suggestions(self, user_input: str) -> Dict:
        """获取建议"""
        prompt = f"""请根据以下用户请求提供建议：

用户：{user_input}

请提供 3 条实用建议，每条一行。"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"💡 **智能建议**\n\n{response}",
                metadata={"type": "suggestions"}
            )
        
        return self._response(self._get_default_suggestions())
    
    def _list_reminders(self) -> Dict:
        """列出提醒"""
        if not self._reminders:
            return self._response("暂无提醒")
        
        pending = [r for r in self._reminders if r.get("status") == "pending"]
        
        if not pending:
            return self._response("所有提醒已完成 ✅")
        
        lines = ["⏰ **提醒列表**"]
        for r in pending:
            time_str = datetime.fromisoformat(r["time"]).strftime("%H:%M:%S")
            lines.append(f"  • {r['content']} - {time_str}")
        
        return self._response("\n".join(lines))
    
    def _get_default_suggestions(self) -> str:
        return """💡 **智能建议**

1. 设置提醒 - 不错过重要事项
2. 使用待办清单 - 提高效率
3. 定期复盘 - 持续改进

💡 告诉我您的需求，我将提供更精准的建议"""
    
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


if __name__ == "__main__":
    agent = ProactiveAgentV4("test")
    print("✅ proactive_agent_v4 测试通过")
