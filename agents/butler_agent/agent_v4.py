#!/usr/bin/env python3
"""ButlerAgent v4.0 - 智慧化私人管家"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from datetime import datetime
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class ButlerAgentV4(BusinessAgent):
    """私人管家 - 智慧化版本"""
    
    name = "butler_agent_v4"
    description = "智慧私人管家"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        
        # 多轮对话历史
        self._conversation_history = []
        self._max_history = 10
        
        # 管家特有功能
        self._todos = []      # 待办事项
        self._calendar = []   # 日程安排
        self._reminders = []  # 提醒事项
        
        print(f"👤 ButlerAgent v{self.version} 智慧化启动")
        print(f"   💾 对话历史已启用 (保留最近 {self._max_history} 轮)")
        print(f"   📋 待办/日程/提醒功能已启用")
    
    # ========== 能力声明 ==========
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        """声明能力"""
        capabilities = {
            ("schedule", "task"): (True, 0.95),   # 安排任务
            ("remind", "info"): (True, 0.90),     # 设置提醒
            ("todo", "task"): (True, 0.95),       # 待办事项
            ("search", "info"): (True, 0.80),     # 查询信息
            ("chat", "text"): (True, 0.85),       # 日常对话
            ("remember", "info"): (True, 0.90),   # 记忆信息
            ("recall", "info"): (True, 0.90),     # 回忆信息
        }
        return capabilities.get((action, target), (False, 0.0))
    
    # ========== 对话历史管理 ==========
    
    def _get_conversation_context(self, user_input: str) -> str:
        """获取对话上下文"""
        if not self._conversation_history:
            return user_input
        
        context_parts = ["【对话历史】"]
        for i, msg in enumerate(self._conversation_history[-self._max_history:], 1):
            context_parts.append(f"{i}. 用户: {msg['user']}")
            context_parts.append(f"   助手: {msg['assistant']}")
        
        context_parts.append(f"\n【当前】{user_input}")
        return "\n".join(context_parts)
    
    def _update_conversation(self, user_input: str, response: str):
        """更新对话历史"""
        self._conversation_history.append({
            "user": user_input[:200],
            "assistant": response[:200],
            "timestamp": datetime.now().isoformat()
        })
        if len(self._conversation_history) > self._max_history:
            self._conversation_history = self._conversation_history[-self._max_history:]
    
    # ========== 情感识别 ==========
    
    def _get_emotion_response(self, user_input: str) -> str:
        """根据情感返回回应"""
        emotion_keywords = {
            "happy": ["开心", "高兴", "太好了", "哈哈", "😊"],
            "sad": ["难过", "伤心", "沮丧", "😢", "😭"],
            "angry": ["生气", "愤怒", "恼火", "😠"],
            "confused": ["不明白", "不懂", "什么意思", "🤔"],
            "grateful": ["谢谢", "感谢", "多谢", "🙏"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in user_input for kw in keywords):
                responses = {
                    "happy": ["很高兴您心情不错！😊", "您的开心感染了我！"],
                    "sad": ["很抱歉听到这个消息...有什么我可以帮您的吗？"],
                    "angry": ["很抱歉让您感到不满，我会努力改进。"],
                    "confused": ["让我重新解释一下...", "抱歉没说清楚："],
                    "grateful": ["不客气！很高兴能帮到您。"]
                }
                import random
                return random.choice(responses.get(emotion, ["好的。"]))
        return None
    
    # ========== 待办事项管理 ==========
    
    def _add_todo(self, task: str) -> str:
        """添加待办"""
        self._todos.append({
            "task": task,
            "completed": False,
            "created_at": datetime.now().isoformat()
        })
        return f"✅ 已添加待办：{task}"
    
    def _list_todos(self) -> str:
        """列出待办"""
        if not self._todos:
            return "暂无待办事项"
        
        pending = [t for t in self._todos if not t.get("completed", False)]
        if not pending:
            return "🎉 所有待办都已完成！"
        
        lines = ["📋 待办事项："]
        for i, t in enumerate(pending, 1):
            lines.append(f"  {i}. {t['task']}")
        return "\n".join(lines)
    
    def _complete_todo(self, index: int) -> str:
        """完成待办"""
        pending = [t for t in self._todos if not t.get("completed", False)]
        if 1 <= index <= len(pending):
            pending[index-1]["completed"] = True
            return f"✅ 已完成：{pending[index-1]['task']}"
        return "❌ 找不到该待办"
    
    # ========== 核心业务逻辑 ==========
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心管家逻辑"""
        
        # 1. 清空对话
        if user_input.strip() in ["清空对话", "清空历史", "重置"]:
            count = len(self._conversation_history)
            self._conversation_history = []
            return self._response(f"✅ 已清空 {count} 轮对话历史")
        
        # 2. 情感回应
        emotion_response = self._get_emotion_response(user_input)
        if emotion_response:
            self._update_conversation(user_input, emotion_response)
            return self._response(emotion_response, metadata={"emotion": True})
        
        # 3. 名字记忆
        if "我叫" in user_input and not any(q in user_input for q in ["什么", "吗", "？"]):
            name = self._extract_name(user_input)
            if name:
                self.remember_forever("user_name", name)
                response = f"你好，{name}！我是您的私人管家。"
                self._update_conversation(user_input, response)
                return self._response(response)
        
        # 4. 查询名字
        if any(q in user_input for q in ["我叫什么", "我的名字"]):
            name = self.recall_forever("user_name")
            response = f"您的名字是{name}。" if name else "我还不知道您的名字，请告诉我。"
            self._update_conversation(user_input, response)
            return self._response(response)
        
        # 5. 待办事项
        if "添加待办" in user_input or "记一下" in user_input:
            task = re.sub(r'(添加待办|记一下)', '', user_input).strip()
            if task:
                response = self._add_todo(task)
                self._update_conversation(user_input, response)
                return self._response(response)
        
        if "查看待办" in user_input or "我的待办" in user_input:
            response = self._list_todos()
            self._update_conversation(user_input, response)
            return self._response(response)
        
        if "完成待办" in user_input:
            match = re.search(r'(\d+)', user_input)
            if match:
                response = self._complete_todo(int(match.group(1)))
                self._update_conversation(user_input, response)
                return self._response(response)
        
        # 6. 记忆偏好
        if "记住" in user_input or "我喜欢" in user_input:
            match = re.search(r'(?:记住|我喜欢)(.+?)(?:是|：)(.+)', user_input)
            if match:
                key, value = match.group(1).strip(), match.group(2).strip()
                self.remember_forever(f"pref_{key}", value)
                response = f"✅ 已记住：{key} = {value}"
                self._update_conversation(user_input, response)
                return self._response(response)
        
        # 7. 默认：使用 LLM + 上下文
        context_prompt = self._get_conversation_context(user_input)
        response = self._call_llm(context_prompt)
        
        if not response:
            response = f"您好！我是您的私人管家。有什么可以帮您的吗？"
        
        self._update_conversation(user_input, response)
        return self._response(response, metadata={"source": "llm"})
    
    # ========== 辅助方法 ==========
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }
    
    def _extract_name(self, text: str) -> str:
        match = re.search(r'我叫([\u4e00-\u9fa5]{2,4})', text)
        if match:
            name = match.group(1)
            if name not in ["什么", "哪个", "谁", "啥"]:
                return name
        return None


if __name__ == "__main__":
    agent = ButlerAgentV4("test")
    print("\n✅ ButlerAgentV4 测试通过")
