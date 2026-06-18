#!/usr/bin/env python3
"""ButlerAgent v4.2 - 精简稳定版（私人管家）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent
from core.lib.dialect.dialect_helper import get_dialect_helper


class ButlerAgentV4(BusinessAgent):
    """私人管家 - 精简稳定版"""

    name = "butler_agent_v4"
    description = "智慧私人管家"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._todos = []
        self._conversation_history = []
        self._max_history = 10
        print(f"👤 ButlerAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        original = user_input
        user_name = self.recall_forever("user_name")
        
        # ========== 1. 名字学习 ==========
        name_match = re.search(r'(?:叫我|我叫|可以叫我|称呼我|以后叫我)\s*([^\s，,。.!！?？]+)', original)
        if name_match:
            name = name_match.group(1)
            if name and name not in ["什么", "啥", "谁", "哪", "怎么"]:
                self.remember_forever("user_name", name)
                return self._resp(f"好的主人，我记住啦！以后就叫您{name}~ 😊")
        
        # ========== 2. 查询名字 ==========
        if any(kw in original for kw in ["我叫什么", "我的名字", "我叫啥", "我是谁"]):
            if user_name:
                return self._resp(f"您叫{user_name}呀，主人~ 😊")
            return self._resp("我还不知道您的名字呢，可以告诉我吗？")
        
        # ========== 3. 待办 ==========
        # 添加待办
        if any(kw in original for kw in ["添加待办", "记一下", "提醒我"]):
            task = re.sub(r'(添加待办|记一下|提醒我)', '', original).strip()
            if task:
                self._todos.append({"task": task, "completed": False, "created_at": datetime.now().isoformat()})
                return self._resp(f"✅ 已添加待办：{task}")
            return self._resp("请告诉我需要添加什么待办事项。")
        
        # 查看待办
        if any(kw in original for kw in ["查看待办", "我的待办", "待办列表", "有哪些待办"]):
            pending = [t for t in self._todos if not t.get("completed", False)]
            if pending:
                lines = ["📋 待办事项："]
                for i, t in enumerate(pending, 1):
                    lines.append(f"  {i}. {t['task']}")
                return self._resp("\n".join(lines))
            return self._resp("🎉 所有待办都已完成！")
        
        # 完成待办
        if any(kw in original for kw in ["完成待办", "已完成", "搞定"]):
            match = re.search(r'(\d+)', original)
            if match:
                idx = int(match.group(1)) - 1
                pending = [t for t in self._todos if not t.get("completed", False)]
                if 0 <= idx < len(pending):
                    pending[idx]["completed"] = True
                    return self._resp(f"✅ 已完成：{pending[idx]['task']}")
            return self._resp("请提供待办编号。例如：完成待办 1")
        
        # ========== 4. 清空对话 ==========
        if any(kw in original for kw in ["清空对话", "清空历史", "重置对话"]):
            self._conversation_history = []
            return self._resp("✅ 已清空对话历史")
        
        # ========== 5. 情感回应 ==========
        emotion_resp = self._get_emotion_response(original)
        if emotion_resp:
            self._update_history(original, emotion_resp)
            return self._resp(emotion_resp)
        
        # ========== 6. 默认对话 ==========
        prompt = f"你是私人管家，简短回复：{original}"
        response = self._call_llm(prompt)
        if not response:
            response = "您好！我是您的私人管家，有什么可以帮您的吗？"
        
        self._update_history(original, response)
        return self._resp(response)

    # ================================================================
    #  辅助方法
    # ================================================================

    def _get_emotion_response(self, text: str) -> Optional[str]:
        if "开心" in text or "高兴" in text:
            return "很高兴您心情不错！有什么需要我帮忙的吗？😊"
        if "谢谢" in text or "感谢" in text:
            return "不客气！很高兴能帮到您。"
        if "难过" in text or "伤心" in text:
            return "很抱歉听到这个消息...希望您能好起来。"
        return None

    def _update_history(self, user_input: str, response: str):
        self._conversation_history.append({
            "user": user_input[:200],
            "assistant": response[:200],
            "timestamp": datetime.now().isoformat()
        })
        if len(self._conversation_history) > self._max_history:
            self._conversation_history = self._conversation_history[-self._max_history:]

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 150}
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[Butler] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = ButlerAgentV4("test")
    print(agent.process("我叫王小明")["response"])
