#!/usr/bin/env python3
"""Butler V4 - Butler V4 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from core.butler.memory_manager import SmartMemoryManager
from core.butler.llm_client import SmartLLMClient


class ButlerV4:
    """私人管家 v4.0 - 智能、主动、人性化"""
    
    VERSION = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.config = self._load_config()

        # 初始化组件
        self.memory = SmartMemoryManager(user_id)
        self.llm = SmartLLMClient()

        # 管家状态
        self.name = self._load_name()
        self.last_active = datetime.now()

        # 主动服务
        self.proactive_enabled = self.config.get('features', {}).get('proactive', {}).get('enabled', True)

        print(f"👤 私人管家 v{self.VERSION} 已启动 (用户: {user_id})")
        print(f"   LLM: {self.llm.model if self.llm.is_available() else '不可用'}")
    
    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = Path("config/butler/butler.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_name(self) -> str:
        """加载管家名称"""
        name = self.memory.recall_preference("butler_name")
        if not name:
            name = self.config.get('identity', {}).get('default_name', '小管')
        return name
    
    def _save_name(self, new_name: str):
        """保存管家名称"""
        self.name = new_name
        self.memory.remember_preference("butler_name", new_name)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        identity = self.config.get('identity', {})
        personality = self.config.get('personality', {})
        communication = self.config.get('communication', {})

        # 获取用户画像
        preferences = self.memory.preferences
        pref_text = ""
        if preferences:
            pref_items = [f"- {k}: {v}" for k, v in preferences.items() if k != 'butler_name']
            if pref_items:
                pref_text = f"\n\n用户偏好:\n" + "\n".join(pref_items)

        # 获取待办
        todos = self.memory.recall_preference("todos") or []
        pending = [t for t in todos if not t.get('done', False)]
        todo_text = ""
        if pending:
            todo_list = "\n".join([f"  • {t['task']}" for t in pending[:5]])
            todo_text = f"\n\n待办事项:\n{todo_list}"

        return f"""你是 {self.name}，{identity.get('role', '私人管家')}。

人格特质：{', '.join(personality.get('traits', ['体贴', '忠诚', '细心']))}
沟通风格：{communication.get('style', '温柔关怀')}
座右铭：{identity.get('motto', '您的信任，我的使命')}

{pref_text}{todo_text}

规则：
1. 你就是 {self.name}，不是其他 AI 助手
2. 回答要{communication.get('style', '温柔关怀')}
3. 优先使用用户偏好信息
4. 如有待办，可主动提醒
5. 保持简洁、有用、贴心"""

    def _build_messages(self, user_input: str) -> List[Dict]:
        """构建消息列表"""
        messages = [{"role": "system", "content": self._get_system_prompt()}]

        # 添加对话历史
        history = self.memory.get_conversation_context(limit=10)
        for h in history:
            # 解析历史记录
            content = h.get('content', '')
            if '用户: ' in content and '管家: ' in content:
                parts = content.split('\n')
                for part in parts:
                    if part.startswith('用户: '):
                        messages.append({"role": "user", "content": part[4:]})
                    elif part.startswith('管家: '):
                        messages.append({"role": "assistant", "content": part[4:]})

        # 添加当前消息
        messages.append({"role": "user", "content": user_input})

        return messages
    
    def _handle_todo(self, user_input: str) -> Optional[Dict]:
        """处理待办"""
        todos = self.memory.recall_preference("todos") or []

        # 添加待办
        if "记住" in user_input or "提醒我" in user_input:
            task = user_input
            for kw in ["记住", "提醒我", "添加待办", "帮我记住"]:
                task = task.replace(kw, "")
            task = task.strip()
            if task:
                todos.append({
                    "task": task,
                    "done": False,
                    "created_at": datetime.now().isoformat()
                })
                self.memory.remember_preference("todos", todos)
                return {"response": f"✅ 已记住：{task}", "type": "todo_add"}

        # 查询待办
        if "待办" in user_input or "有什么任务" in user_input:
            pending = [t for t in todos if not t.get('done', False)]
            if pending:
                tasks = "\n".join([f"  • {t['task']}" for t in pending[:10]])
                return {"response": f"您有 {len(pending)} 个待办事项：\n{tasks}", "todos": pending, "type": "todo_list"}
            return {"response": "您暂时没有待办事项", "type": "todo_empty"}

        # 完成待办
        if "完成" in user_input and "待办" in user_input:
            return {"response": "请告诉我要完成哪个待办", "type": "todo_complete_ask"}

        return None
    
    def _handle_preference(self, user_input: str) -> Optional[Dict]:
        """处理偏好"""
        if "喜欢" in user_input:
            import re
            match = re.search(r'喜欢(.+?)(?:[，。！？]|$)', user_input)
            if match:
                value = match.group(1).strip()
                if value and len(value) < 30:
                    self.memory.remember_preference("likes", value)
                    return {"response": f"💖 已记住您喜欢{value}", "type": "preference_save"}

        if "我的偏好" in user_input or "我喜欢什么" in user_input:
            likes = self.memory.recall_preference("likes")
            if likes:
                return {"response": f"根据记录，您喜欢{likes}", "likes": likes, "type": "preference_query"}
            return {"response": "我还没有记住您的偏好，可以告诉我'我喜欢xxx'", "type": "preference_empty"}

        return None
    
    def _handle_rename(self, user_input: str) -> Optional[Dict]:
        """处理改名"""
        patterns = ["叫我", "以后叫我", "改名叫", "你的名字叫"]
        for pattern in patterns:
            if pattern in user_input:
                new_name = user_input.split(pattern)[-1].strip()[:10]
                if new_name:
                    self._save_name(new_name)
                    return {"response": f"✨ 好的，以后请叫我 {new_name}", "new_name": new_name, "type": "rename"}
        return None
    
    def process(self, user_input: str) -> Dict:
        """处理用户输入 - 主入口"""
        # 1. 改名
        rename_result = self._handle_rename(user_input)
        if rename_result:
            self.memory.add_conversation(user_input, rename_result['response'])
            return rename_result

        # 2. 待办
        todo_result = self._handle_todo(user_input)
        if todo_result:
            self.memory.add_conversation(user_input, todo_result['response'])
            return todo_result

        # 3. 偏好
        pref_result = self._handle_preference(user_input)
        if pref_result:
            self.memory.add_conversation(user_input, pref_result['response'])
            return pref_result

        # 4. LLM 对话
        messages = self._build_messages(user_input)

        if self.llm.is_available():
            response = self.llm.chat(messages)
        else:
            response = self._fallback_response(user_input)

        # 5. 记录对话
        self.memory.add_conversation(user_input, response)

        return {
            "success": True,
            "response": response,
            "user_id": self.user_id,
            "butler_name": self.name
        }
    
    def _fallback_response(self, user_input: str) -> str:
        """备用响应"""
        butler_name = self.name
        return f"您好！我是{butler_name}，您的私人管家。有什么可以帮您的？"
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "version": self.VERSION,
            "user_id": self.user_id,
            "butler_name": self.name,
            "memory": self.memory.get_stats(),
            "llm_available": self.llm.is_available()
        }


# 创建工厂函数
def create_butler(user_id: str = "default") -> ButlerV4:
    """创建私人管家实例"""
    return ButlerV4(user_id)
