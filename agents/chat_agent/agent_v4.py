#!/usr/bin/env python3
"""ChatAgent v4.2 - 稳定可靠版"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
import time
import threading
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Callable
from collections import deque

from core.agents.business.business_agent import BusinessAgent
from core.lib.dialect.dialect_helper import get_dialect_helper


class ChatAgentV4(BusinessAgent):
    """
    聊天 Agent - 稳定可靠版
    
    核心特性:
    1. 输入缓冲（防抖）：等待用户输入完整后再处理
    2. LLM 重试机制：失败自动重试
    3. 降级方案：LLM 不可用时仍有友好回复
    4. 方言支持：自动识别和转换方言
    5. 记忆系统：记住用户名字和偏好
    """

    name = "chat_agent_v4"
    description = "智慧对话助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        
        # ========== 对话历史 ==========
        self._history: List[Dict] = []
        self._max_history = 10
        
        # ========== 输入缓冲（防抖）==========
        self._input_buffer: List[str] = []
        self._buffer_timer: Optional[threading.Timer] = None
        self._buffer_lock = threading.Lock()
        self._buffer_wait = 2.0  # 等待 2 秒无新输入再处理
        self._buffer_pending = False
        self._on_buffer_flush: Optional[Callable] = None
        
        # ========== 用户状态 ==========
        self._user_name: Optional[str] = None
        self._last_input: Optional[str] = None
        self._last_response: Optional[str] = None
        
        # ========== 方言 ==========
        self._dialect = get_dialect_helper(user_id)
        
        # ========== LLM 配置 ==========
        self._llm_model = "qwen2:1.5b-instruct"
        self._llm_timeout = 30
        self._max_retries = 2
        
        print(f"💬 ChatAgent v{self.version} 启动")
        print(f"   📦 输入缓冲: {self._buffer_wait}s")
        print(f"   🔄 LLM 重试: {self._max_retries} 次")

    # ================================================================
    #  核心入口
    # ================================================================

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        处理用户输入（同步模式）
        用于直接调用，不经过缓冲
        """
        return self._handle_input(user_input)

    def feed(self, text: str, callback: Optional[Callable] = None):
        """
        流式输入（带缓冲）
        用户连续输入时，等待 2 秒无新输入再触发处理
        """
        with self._buffer_lock:
            self._input_buffer.append(text)
            self._buffer_pending = True
            
            if callback:
                self._on_buffer_flush = callback
            
            # 重置计时器
            if self._buffer_timer:
                self._buffer_timer.cancel()
            
            self._buffer_timer = threading.Timer(self._buffer_wait, self._flush_buffer)
            self._buffer_timer.daemon = True
            self._buffer_timer.start()

    def _flush_buffer(self):
        """缓冲时间到，合并输入并处理"""
        with self._buffer_lock:
            if not self._buffer_pending:
                return
            
            full_input = " ".join(self._input_buffer).strip()
            self._input_buffer.clear()
            self._buffer_pending = False
            
            if not full_input:
                return
            
            result = self._handle_input(full_input)
            
            if self._on_buffer_flush:
                self._on_buffer_flush(result)
            else:
                # 默认返回给调用方
                self._last_response = result

    # ================================================================
    #  核心处理逻辑
    # ================================================================

    def _handle_input(self, user_input: str) -> Dict:
        """处理完整输入"""
        original = user_input
        self._last_input = original
        
        # ========== 1. 加载用户记忆 ==========
        self._user_name = self.recall_forever("user_name")
        
        # ========== 2. 方言转换 ==========
        has_dialect = self._dialect.has_dialect(user_input)
        if has_dialect:
            user_input, _ = self._dialect.to_standard(user_input)
            print(f"[方言] {original} → {user_input}")
        
        # ========== 3. 特殊命令（不走 LLM，保证稳定性）==========
        response = self._handle_special(original, user_input)
        if response:
            self._update_history(original, response)
            return self._resp(response)
        
        # ========== 4. LLM 处理（带重试）==========
        response = self._call_llm_with_retry(user_input)
        
        if not response:
            response = self._fallback(user_input)
        
        # ========== 5. 方言回译 ==========
        if has_dialect and response:
            response, _ = self._dialect.to_dialect(response)
        
        # ========== 6. 更新历史 ==========
        self._update_history(original, response)
        
        return self._resp(response)

    # ================================================================
    #  特殊命令（不走 LLM）
    # ================================================================

    def _handle_special(self, original: str, normalized: str) -> Optional[str]:
        """处理特殊命令，返回响应或 None"""
        # 清空对话
        if normalized.strip() in ["清空", "重置", "clear"]:
            self._history = []
            return "✅ 已清空对话历史"
        
        # 查询名字
        if any(q in normalized for q in ["我叫什么", "我的名字", "还记得我吗", "我是谁"]):
            if self._user_name:
                return f"当然记得！你叫 {self._user_name} 😊"
            return "我还不知道你的名字呢，可以告诉我吗？"
        
        # 学习名字
        name_match = re.search(r'(?:我叫|叫我|英文名)[：: ]*(\S+)', original)
        if name_match:
            name = name_match.group(1)
            if name and len(name) <= 6 and name not in ["什么", "啥", "谁", "吗"]:
                self.remember_forever("user_name", name)
                self._user_name = name
                return f"好的，我记住你叫 {name} 了！😊"
        
        # 学习方言
        if "就是" in normalized or "意思是" in normalized:
            match = re.search(r'(\S+)\s+(?:就是|意思是)\s+(.+)', original)
            if match:
                self._dialect.learn_direct(match.group(1), match.group(2))
                return f"学到啦！「{match.group(1)}」是「{match.group(2)}」的意思~ 😊"
        
        # 天气
        if any(kw in normalized for kw in ["天气", "温度", "下雨", "晴天"]):
            return "我暂时查不了实时天气呢~ 你可以告诉我你那里的天气 ☀🌧"
        
        return None

    # ================================================================
    #  LLM 调用（带重试）
    # ================================================================

    def _call_llm_with_retry(self, user_input: str) -> Optional[str]:
        """带重试的 LLM 调用"""
        for attempt in range(self._max_retries):
            try:
                prompt = self._build_prompt(user_input)
                result = self._call_llm(prompt)
                if result and len(result) > 3:
                    return result
                print(f"[ChatAgent] 尝试 {attempt+1}/{self._max_retries} 返回空结果")
            except Exception as e:
                print(f"[ChatAgent] 尝试 {attempt+1}/{self._max_retries} 失败: {e}")
                time.sleep(0.5 * (attempt + 1))  # 递增等待
        
        return None

    def _build_prompt(self, user_input: str) -> str:
        """构建 Prompt"""
        history = self._get_history_text()
        name_hint = f"用户叫 {self._user_name}。" if self._user_name else ""
        
        return f"""你是小爪，ClawsJoy 的聊天助手。

{name_hint}
{history}
用户说：{user_input}

小爪简短自然回复："""

    def _get_history_text(self) -> str:
        """获取对话历史文本"""
        if not self._history:
            return ""
        
        recent = self._history[-6:]
        parts = []
        for h in recent:
            user = h.get("user", "")
            assistant = h.get("assistant", "")
            if user:
                parts.append(f"用户：{user}")
            if assistant and assistant != "[处理中]":
                parts.append(f"小爪：{assistant}")
        
        return "最近对话：\n" + "\n".join(parts) + "\n" if parts else ""

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        import requests
        
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self._llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 120
                }
            },
            timeout=self._llm_timeout
        )
        
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        
        raise Exception(f"LLM 返回错误: {resp.status_code}")

    # ================================================================
    #  降级方案
    # ================================================================

    def _fallback(self, user_input: str) -> str:
        """LLM 不可用时的降级回复"""
        if self._user_name:
            return f"{self._user_name}，我没理解清楚，能再说一遍吗？😊"
        return "我没太明白，能再说一遍吗？😊"

    # ================================================================
    #  辅助方法
    # ================================================================

    def _update_history(self, user_input: str, response: str):
        self._history.append({
            "user": user_input[:200],
            "assistant": response[:200],
            "timestamp": datetime.now().isoformat()
        })
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def _resp(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.9)


if __name__ == "__main__":
    agent = ChatAgentV4("test")
    
    # 同步测试
    print("=== 同步测试 ===")
    result = agent.process("你好")
    print(result["response"])
    
    # 缓冲测试（模拟打字）
    print("\n=== 缓冲测试 ===")
    print("模拟用户输入: '今天' -> 等待 -> '天气' -> 2秒后合并")
    agent.feed("今天")
    time.sleep(1.5)
    agent.feed("天气")
    time.sleep(3)  # 等待缓冲触发
