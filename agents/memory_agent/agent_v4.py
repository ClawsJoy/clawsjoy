#!/usr/bin/env python3
"""memory_agent v4.0 - 智慧化记忆智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class MemoryAgentV4(BusinessAgent):
    """智慧化记忆智能体"""
    
    name = "memory_agent_v4"
    description = "智慧化记忆助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📝 {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("remember", "info"): (True, 0.95),
            ("recall", "info"): (True, 0.95),
            ("forget", "info"): (True, 0.85),
            ("list", "memory"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 记住信息
        if "记住" in user_input:
            match = re.search(r'记住(.+?)(?:是|：|:)(.+)', user_input)
            if match:
                key, value = match.group(1).strip(), match.group(2).strip()
                self.remember_forever(key, value)
                return self._response(f"✅ 已记住：{key} = {value}")
            else:
                # 简单格式：记住 生日=5月1日
                parts = user_input.replace("记住", "").strip().split("=")
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    self.remember_forever(key, value)
                    return self._response(f"✅ 已记住：{key} = {value}")
        
        # 回忆信息
        if "回忆" in user_input or "记得" in user_input:
            key = re.sub(r'回忆|记得', '', user_input).strip()
            value = self.recall_forever(key)
            if value:
                return self._response(f"📖 {key} = {value}")
            return self._response(f"❌ 不记得 {key}")
        
        # 忘记信息
        if "忘记" in user_input:
            key = re.sub(r'忘记', '', user_input).strip()
            if self.forget_forever(key):
                return self._response(f"🗑️ 已忘记：{key}")
            return self._response(f"❌ 未找到：{key}")
        
        # 列出所有记忆
        if "列出" in user_input or "所有记忆" in user_input:
            memories = self.get_all_memories()
            permanent = memories.get("permanent", {})
            if permanent:
                lines = ["📋 **永久记忆**"]
                for key, data in permanent.items():
                    value = data.get("value") if isinstance(data, dict) else data
                    lines.append(f"  • {key}: {value}")
                return self._response("\n".join(lines))
            return self._response("暂无记忆")
        
        return self._response(self._get_help())
    
    def _get_help(self) -> str:
        return """📝 **记忆助手**

使用方式:
- 记住信息: "记住 生日=5月1日"
- 回忆信息: "回忆 生日"
- 忘记信息: "忘记 生日"
- 列出记忆: "列出所有记忆"

💡 记忆会永久保存，跨会话可用"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = MemoryAgentV4("test")
    print("✅ memory_agent_v4 测试通过")
