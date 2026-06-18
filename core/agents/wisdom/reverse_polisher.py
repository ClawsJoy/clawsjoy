#!/usr/bin/env python3
"""LLM 逆向润色器 - 所有 Agent 共享，让系统输出像人话"""

import json
import re
from typing import Dict, Optional


class ReversePolisher:
    """逆向润色器 - 把系统输出翻译成用户能理解的语言"""

    def __init__(self, llm_caller=None):
        self._llm = llm_caller
        self._model = "qwen2:1.5b-instruct"  # 🆕 轻量快速
        self._max_tokens = 256
        self._timeout = 20
    
    def polish(
        self,
        raw_response: str,
        user_input: str,
        agent_name: str = None,
        session_id: str = None,
        extra_context: dict = None
    ) -> str:
        """润色系统输出"""
        if not raw_response:
            return ""

        # 如果已经是自然语言（检测到对话特征），跳过润色
        if self._is_natural(raw_response):
            return raw_response

        # 构建润色提示词
        prompt = self._build_prompt(
            raw_response, user_input, agent_name, session_id, extra_context
        )

        # 调用 LLM 润色
        polished = self._call_llm(prompt)

        return polished or raw_response

    def _is_natural(self, text: str) -> bool:
        """判断是否已经是自然语言"""
        natural_patterns = [
            r'^(我|你|他|她|它|我们|你们)',
            r'^(好|行|嗯|对|是)',
            r'^(明白|知道|了解|清楚)',
        ]
        for pattern in natural_patterns:
            if re.search(pattern, text.strip(), re.IGNORECASE):
                return True
        return False

    def _build_prompt(
        self,
        raw: str,
        user_input: str,
        agent_name: str,
        session_id: str,
        extra_context: dict
    ) -> str:
        """构建润色提示词"""
        agent_display = {
            'code_agent': '代码助手',
            'writer_agent': '作家助手',
            'director_agent': '导演助手',
            'chat_agent': '聊天助手',
        }.get(agent_name, '助手')

        # 提取用户情绪
        emotion = self._detect_emotion(user_input)

        context_info = ""
        if extra_context:
            if extra_context.get('user_level'):
                context_info += f"\n- 用户水平: {extra_context.get('user_level')}"
            if extra_context.get('task_type'):
                context_info += f"\n- 任务类型: {extra_context.get('task_type')}"

        return f"""
你是一个专业的翻译官，负责把{agent_display}的输出翻译成用户能理解的语言。

## {agent_display}的原始输出
{raw}

## 用户刚才说
{user_input}

## 用户情绪
{emotion}

## 上下文
- Agent: {agent_name}{context_info}

## 翻译要求
1. 信息完整，不丢失关键内容
2. 语言自然、友好、口语化
3. 专业术语用通俗语言解释
4. 根据用户情绪调整语气（焦虑→温和，急切→简洁）
5. 结尾引导用户下一步可以做什么

## 输出
直接输出翻译后的内容，不要加任何前缀：
"""

    def _detect_emotion(self, text: str) -> str:
        """简单检测用户情绪"""
        if any(w in text for w in ['急', '快', '马上', '赶紧', '帮帮我']):
            return '急切'
        if any(w in text for w in ['难', '烦', '不懂', '不会']):
            return '焦虑'
        if any(w in text for w in ['好', '谢谢', '感谢']):
            return '积极'
        return '中性'

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        if self._llm:
            return self._llm(prompt)

        # 降级：使用系统默认 LLM
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except:
            pass
        return ""
