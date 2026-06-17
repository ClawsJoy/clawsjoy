#!/usr/bin/env python3
"""memory_agent v4.1 - 智慧化记忆智能体（自然语言增强版）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class MemoryAgentV4(BusinessAgent):
    """智慧化记忆智能体 - 支持自然语言交互"""

    name = "memory_agent_v4"
    description = "智慧化记忆助手"
    version = "4.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        # 常用记忆键映射
        self._key_mappings = {
            "名字": "名字", "姓名": "名字", "叫什么": "名字",
            "喜欢": "喜欢", "喜好": "喜欢", "爱好": "喜欢",
            "颜色": "颜色", "生日": "生日", "年龄": "年龄",
            "城市": "城市", "家乡": "家乡", "职业": "职业"
        }
        print(f"📝 {self.name} v{self.version} 智慧化启动（自然语言增强版）")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("remember", "info"): (True, 0.95),
            ("recall", "info"): (True, 0.95),
            ("forget", "info"): (True, 0.85),
            ("list", "memory"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心记忆逻辑 - 支持自然语言"""

        # ========== 1. 记住信息 ==========
        if any(kw in user_input for kw in ["记住", "保存", "存储", "我喜欢", "我叫", "我的", "名字是"]):
            result = self._handle_remember(user_input)
            if result:
                return result

        # ========== 2. 回忆信息 ==========
        if any(kw in user_input for kw in ["回忆", "记得", "查询", "找", "我的", "什么", "哪个"]):
            result = self._handle_recall(user_input)
            if result:
                return result

        # ========== 3. 忘记信息 ==========
        if any(kw in user_input for kw in ["忘记", "删除", "清除"]):
            result = self._handle_forget(user_input)
            if result:
                return result

        # ========== 4. 列出所有记忆 ==========
        if any(kw in user_input for kw in ["列出", "所有", "全部"]):
            return self._handle_list()

        # ========== 5. 默认帮助 ==========
        return self._response(self._get_help())

    def _handle_remember(self, user_input: str) -> Optional[Dict]:
        """处理记忆请求 - 支持多种格式"""
        # 如果是问句，不记忆
        if any(kw in user_input for kw in ["什么", "吗", "？", "?"]):
            return None
        # 格式1: 记住 key=value
        match = re.search(r'(?:记住|保存)\s*(.+?)\s*[=是：:]\s*(.+)', user_input)
        if match:
            key, value = match.group(1).strip(), match.group(2).strip()
            self.remember_forever(key, value)
            return self._response(f"✅ 已记住：{key} = {value}")
        
        # 格式2: 我喜欢蓝色 -> 喜欢=蓝色
        if "我喜欢" in user_input:
            value = user_input.replace("我喜欢", "").strip()
            if value:
                self.remember_forever("喜欢", value)
                return self._response(f"✅ 已记住：喜欢 = {value}")
        
        # 格式3: 我叫张三 / 名字是张三
        if "我叫" in user_input or "名字是" in user_input:
            match = re.search(r'(?:我叫|名字是)\s*([\u4e00-\u9fa5a-zA-Z\s]+)', user_input)
            if match:
                name = match.group(1).strip()
                self.remember_forever("名字", name)
                return self._response(f"✅ 已记住：名字 = {name}")
        
        # 格式4: 我的生日是5月1日
        if "我的" in user_input and "是" in user_input:
            match = re.search(r'我的(.+?)是(.+)', user_input)
            if match:
                key, value = match.group(1).strip(), match.group(2).strip()
                self.remember_forever(key, value)
                return self._response(f"✅ 已记住：{key} = {value}")
        
        # 格式5: key=value (无记住前缀)
        if "=" in user_input and not any(kw in user_input for kw in ["回忆", "忘记", "列出"]):
            parts = user_input.split("=", 1)
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                self.remember_forever(key, value)
                return self._response(f"✅ 已记住：{key} = {value}")
        
        return None

    def _handle_recall(self, user_input: str) -> Optional[Dict]:
        """处理回忆请求 - 支持模糊匹配"""
        
        # 提取关键词
        key = re.sub(r'(?:回忆|记得|查询|找|一下|我的|什么|哪里|哪个|了|吗|\?)', '', user_input).strip()
        
        # 如果是问句，提取核心词
        if not key or len(key) < 2:
            # 尝试提取名词
            match = re.search(r'(名字|姓名|喜欢|颜色|生日|年龄|城市|家乡|职业|爱好|喜好)', user_input)
            if match:
                key = match.group(1)
        
        if not key:
            return self._response("💡 请告诉我你想回忆什么，比如：回忆 名字")
        
        # 映射到标准键
        mapped_key = self._key_mappings.get(key, key)
        
        # 尝试直接查询
        value = self.recall_forever(mapped_key)
        if value:
            return self._response(f"📖 {mapped_key} = {value}")
        
        # 尝试模糊匹配
        memories = self.get_all_memories().get("permanent", {})
        for k, v in memories.items():
            if key in k or k in key:
                val = v.get("value") if isinstance(v, dict) else v
                return self._response(f"📖 {k} = {val}")
        
        return self._response(f"❌ 不记得「{key}」，请先告诉我：记住 {key}=xxx")

    def _handle_forget(self, user_input: str) -> Optional[Dict]:
        """处理忘记请求"""
        key = re.sub(r'(?:忘记|删除|清除)', '', user_input).strip()
        
        if not key:
            return self._response("💡 请告诉我你想忘记什么，比如：忘记 生日")
        
        if self.forget_forever(key):
            return self._response(f"🗑️ 已忘记：{key}")
        
        # 尝试映射键
        mapped_key = self._key_mappings.get(key, key)
        if mapped_key != key and self.forget_forever(mapped_key):
            return self._response(f"🗑️ 已忘记：{mapped_key}")
        
        return self._response(f"❌ 未找到：{key}")

    def _handle_list(self) -> Dict:
        """列出所有记忆"""
        memories = self.get_all_memories().get("permanent", {})
        
        if not memories:
            return self._response("📭 暂无记忆")
        
        lines = ["📋 **我的记忆**"]
        for key, data in memories.items():
            value = data.get("value") if isinstance(data, dict) else data
            lines.append(f"  •  {key}: {value}")
        
        lines.append(f"\n📊 共 {len(memories)} 条记忆")
        return self._response("\n".join(lines))

