#!/usr/bin/env python3
"""MemoryAgent v4.2 - 精简稳定版（记忆管理）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class MemoryAgentV4(BusinessAgent):
    """记忆 Agent - 精简稳定版"""

    name = "memory_agent_v4"
    description = "智慧记忆助手"
    version = "4.2.0"

    KEY_MAPPINGS = {
        "名字": "名字", "姓名": "名字", "叫什么": "名字",
        "喜欢": "喜欢", "喜好": "喜欢", "爱好": "喜欢",
        "颜色": "颜色", "生日": "生日", "年龄": "年龄",
        "城市": "城市", "家乡": "家乡", "职业": "职业"
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📝 MemoryAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        # 记住
        if any(kw in t for kw in ["记住", "保存", "记一下"]):
            return self._handle_remember(user_input)
        
        # 回忆
        if any(kw in t for kw in ["回忆", "记得", "查询", "找"]):
            return self._handle_recall(user_input)
        
        # 忘记
        if any(kw in t for kw in ["忘记", "删除", "清除"]):
            return self._handle_forget(user_input)
        
        # 列出
        if any(kw in t for kw in ["列出", "所有", "全部"]):
            return self._handle_list()
        
        return self._resp("💡 输入「记住 名字=张三」或「回忆 名字」")

    # ================================================================
    #  记住
    # ================================================================

    def _handle_remember(self, user_input: str) -> Dict:
        # 格式: 记住 名字=张三
        match = re.search(r'(?:记住|保存|记一下)\s*(.+?)\s*[=是：:]\s*(.+)', user_input)
        if match:
            key, value = match.group(1).strip(), match.group(2).strip()
            self.remember_forever(key, value)
            return self._resp(f"✅ 已记住：{key} = {value}")
        
        # 格式: 我喜欢蓝色
        if "我喜欢" in user_input:
            value = user_input.replace("我喜欢", "").strip()
            if value:
                self.remember_forever("喜欢", value)
                return self._resp(f"✅ 已记住：喜欢 = {value}")
        
        # 格式: 我叫张三
        match = re.search(r'(?:我叫|名字是)\s*([\u4e00-\u9fa5a-zA-Z\s]+)', user_input)
        if match:
            name = match.group(1).strip()
            self.remember_forever("名字", name)
            return self._resp(f"✅ 已记住：名字 = {name}")
        
        # 格式: key=value
        if "=" in user_input:
            parts = user_input.split("=", 1)
            key, value = parts[0].strip(), parts[1].strip()
            self.remember_forever(key, value)
            return self._resp(f"✅ 已记住：{key} = {value}")
        
        return self._resp("💡 格式：记住 名字=张三")

    # ================================================================
    #  回忆
    # ================================================================

    def _handle_recall(self, user_input: str) -> Dict:
        key = re.sub(r'(?:回忆|记得|查询|找|一下|我的|什么|了|吗|\?)', '', user_input).strip()
        
        if not key:
            match = re.search(r'(名字|姓名|喜欢|颜色|生日|年龄|城市|家乡|职业)', user_input)
            if match:
                key = match.group(1)
        
        if not key:
            return self._resp("💡 请说：回忆 名字")
        
        mapped_key = self.KEY_MAPPINGS.get(key, key)
        value = self.recall_forever(mapped_key)
        
        if value:
            return self._resp(f"📖 {mapped_key} = {value}")
        
        # 模糊匹配
        memories = self.get_all_memories().get("permanent", {})
        for k, v in memories.items():
            if key in k or k in key:
                val = v.get("value") if isinstance(v, dict) else v
                return self._resp(f"📖 {k} = {val}")
        
        return self._resp(f"❌ 不记得「{key}」")

    # ================================================================
    #  忘记
    # ================================================================

    def _handle_forget(self, user_input: str) -> Dict:
        key = re.sub(r'(?:忘记|删除|清除)', '', user_input).strip()
        if not key:
            return self._resp("💡 请说：忘记 生日")
        
        if self.forget_forever(key):
            return self._resp(f"🗑 已忘记：{key}")
        
        mapped_key = self.KEY_MAPPINGS.get(key, key)
        if mapped_key != key and self.forget_forever(mapped_key):
            return self._resp(f"🗑 已忘记：{mapped_key}")
        
        return self._resp(f"❌ 未找到：{key}")

    # ================================================================
    #  列出
    # ================================================================

    def _handle_list(self) -> Dict:
        memories = self.get_all_memories().get("permanent", {})
        if not memories:
            return self._resp("📭 暂无记忆")
        
        lines = ["📋 我的记忆："]
        for key, data in memories.items():
            value = data.get("value") if isinstance(data, dict) else data
            lines.append(f"  • {key}: {value}")
        lines.append(f"\n共 {len(memories)} 条")
        return self._resp("\n".join(lines))

    # ================================================================
    #  辅助
    # ================================================================

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = MemoryAgentV4("test")
    print(agent.process("记住 名字=张三")["response"])
