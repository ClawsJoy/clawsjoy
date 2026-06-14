#!/usr/bin/env python3
"""ButlerAgent v4.0 - 智慧化私人管家"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import yaml
from pathlib import Path
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent
from core.lib.dialect.dialect_helper import get_dialect_helper  # 方言支持

class ButlerAgentV4(BusinessAgent):
    """私人管家 - 智慧化版本"""
    
    name = "butler_agent_v4"
    description = "智慧私人管家"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        # 加载话本
        self._load_scriptbook()
        # 多轮对话历史
        self._conversation_history = []
        self._max_history = 10
        self._user_profile = {}

        # 管家特有功能
        self._todos = []      # 待办事项
        self._calendar = []   # 日程安排
        self._reminders = []  # 提醒事项
        # 加载已有数据
        self._load_user_data()

        print(f"👤 ButlerAgent v{self.version} 智慧化启动")
        print(f"   💾 对话历史已启用 (保留最近 {self._max_history} 轮)")
        print(f"   📋 待办/日程/提醒功能已启用")
    
    
    def _load_scriptbook(self):
        """加载话本配置"""
        # 优先使用 chat_agent 专用话本
        script_path = Path("config/butler/scriptbook.yaml")
        if not script_path.exists():
            script_path = Path("agents/chat_agent/scriptbook.yaml")
    
        if script_path.exists():
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self._intents = data.get('intents', [])
                    self._templates = data.get('templates', {})
                    print(f"📖 已加载话本: {len(self._intents)} 个意图")
            except Exception as e:
                print(f"话本加载失败: {e}")
        else:
            self._intents = []
            self._templates = {}

    def _match_intent(self, user_input: str) -> str:
        """匹配话本意图"""
        user_lower = user_input.lower()
        for intent in self._intents:
            for keyword in intent.get('keywords', []):
                if keyword in user_lower:
                    return intent.get('response', 'default')
        return 'default'


    def _get_template_response(self, template_name: str, **kwargs) -> str:
        """获取话本回复模板（支持智慧能力注入）"""
        template = self._templates.get(template_name, "")
        if not template:
            return None
    
        # 获取用户画像数据
        user_name = self.recall_forever("user_name")
    
        # 获取待办统计
        todos = getattr(self, '_todos', [])
        todo_count = len([t for t in todos if not t.get("completed", False)])
        completed_count = len([t for t in todos if t.get("completed", False)])
    
        # 构建替换字典
        replacements = {
            "user_name": user_name or "",
            "todo_count": str(todo_count),
            "completed_count": str(completed_count),
            "schedule_count": str(len(getattr(self, '_calendar', []))),
        }
        replacements.update(kwargs)
    
        # 处理 Jinja2 风格的条件语法
        import re
    
        def process_if_block(text):
            pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}'
        
            def replace_if(match):
                var_name = match.group(1)
                true_content = match.group(2)
                false_content = match.group(3) if match.group(3) else ""
            
                if replacements.get(var_name):
                    return true_content
                return false_content
        
            return re.sub(pattern, replace_if, text, flags=re.DOTALL)
    
        result = template
        result = process_if_block(result)
    
        # 简单变量替换
        for key, value in replacements.items():
            if value:
                result = result.replace(f"{{{{{key}}}}}", value)
            else:
                result = result.replace(f"{{{{{key}}}}}", "")
    
        # 清理多余空格
        result = re.sub(r'\n\s*\n', '\n', result)
        result = result.strip()
    
        return result


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
    
    def _load_user_data(self):
        """加载用户数据"""
        # 从持久化存储加载待办事项等
        pass

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心管家逻辑 - 支持方言"""

        # ========== 1. 名字记忆（最高优先级）==========
        # 匹配多种格式
        name_patterns = [
            (r'叫我\s*(\S+)', '叫我'),           # 叫我王总
            (r'我叫\s*(\S+)', '我叫'),           # 我叫王总
            (r'可以叫我\s*(\S+)', '可以叫我'),    # 可以叫我王总
            (r'称呼我\s*(\S+)', '称呼我'),        # 称呼我王总
            (r'以后叫我\s*(\S+)', '以后叫我'),    # 以后叫我王总
        ]

        for pattern, _ in name_patterns:
            import re
            match = re.search(pattern, user_input)
            if match:
                name = match.group(1)
                # 过滤掉疑问词
                if name and name not in ["什么", "啥", "谁", "哪", "怎么"]:
                    self.remember_forever("user_name", name)
                    response = f"好的主人，我记住啦！以后就叫您{name}~ 😊"
                    return self._response(response)
        # 查询名字
        if any(q in user_input for q in ["我叫什么", "我的名字", "我叫啥", "我是谁"]):
            name = self.recall_forever("user_name")
            if name:
                return self._response(f"您叫{name}呀，主人~ 😊")
            else:
                return self._response("我还不知道您的名字呢，可以告诉我吗？")

        # ========== 2. 方言理解 ==========
        dialect_helper = get_dialect_helper(self.user_id)
        original_input = user_input
        has_dialect = dialect_helper.has_dialect(user_input)
    
        if has_dialect:
            user_input, _ = dialect_helper.to_standard(user_input)
            print(f"[ButlerAgent] 方言理解: {original_input} → {user_input}")
    
        # ========== 3. 话本匹配 ==========
        if hasattr(self, '_intents') and self._intents:
            intent_name = self._match_intent(user_input)
            if intent_name:
                # 获取用户变量
                user_name = self.recall_forever("user_name")
                response = self._get_template_response(intent_name, user_name=user_name or "")
                if response:
                    return self._response(response, metadata={"script": True})

        # ========== 4. 清空对话 ==========
        if user_input.strip() in ["清空对话", "清空历史", "重置对话", "clear"]:
            count = len(self._conversation_history)
            self._conversation_history = []
            response = f"✅ 已清空 {count} 轮对话历史"
            if has_dialect:
                dialect_response, _ = dialect_helper.to_dialect(response)
                if dialect_response != response:
                    response = dialect_response
            return self._response(response)

        # ========== 5. 添加待办 ==========
        if "添加待办" in user_input or "记一下" in user_input:
            task = re.sub(r'(添加待办|记一下)', '', user_input).strip()
            if task:
                self._todos.append({
                    "task": task,
                    "completed": False,
                    "created_at": datetime.now().isoformat()
                })
                response = f"✅ 已添加待办：{task}"
                if has_dialect:
                    dialect_response, _ = dialect_helper.to_dialect(response)
                    if dialect_response != response:
                        response = dialect_response
                self._update_conversation(original_input, response)
                return self._response(response)

        # ========== 6. 查看待办 ==========
        if "查看待办" in user_input or "我的待办" in user_input:
            pending = [t for t in self._todos if not t.get("completed", False)]
            if pending:
                lines = ["📋 **待办事项：**"]
                for i, t in enumerate(pending, 1):
                    lines.append(f"  {i}. {t['task']}")
                response = "\n".join(lines)
            else:
                response = "暂无待办事项"
            if has_dialect:
                dialect_response, _ = dialect_helper.to_dialect(response)
                if dialect_response != response:
                    response = dialect_response
            self._update_conversation(original_input, response)
            return self._response(response)

        # ========== 7. 完成待办 ==========
        if "完成待办" in user_input:
            match = re.search(r'(\d+)', user_input)
            if match:
                idx = int(match.group(1)) - 1
                pending = [t for t in self._todos if not t.get("completed", False)]
                if 0 <= idx < len(pending):
                    pending[idx]["completed"] = True
                    response = f"✅ 已完成：{pending[idx]['task']}"
                    if has_dialect:
                        dialect_response, _ = dialect_helper.to_dialect(response)
                        if dialect_response != response:
                            response = dialect_response
                    self._update_conversation(original_input, response)
                    return self._response(response)
        # ========== 8. 情感回应 ==========
        emotion_response = self._get_emotion_response(user_input)
        if emotion_response:
            if has_dialect:
                dialect_response, _ = dialect_helper.to_dialect(emotion_response)
                if dialect_response != emotion_response:
                    emotion_response = dialect_response
            self._update_conversation(original_input, emotion_response)
            return self._response(emotion_response, metadata={"emotion": True})

        # ========== 9. 多轮对话 ==========
        context_prompt = self._get_conversation_context(user_input)
        response = self._call_llm(context_prompt)

        if not response:
            response = f"您好！我是您的私人管家。有什么可以帮您的吗？"

        # ========== 10. 方言回应 ==========
        if has_dialect:
            dialect_response, converted = dialect_helper.to_dialect(response)
            if converted:
                response = dialect_response
                print(f"[ButlerAgent] 方言回应: {dialect_response}")

        self._update_conversation(original_input, response)
        return self._response(response)

    # ========== 辅助方法 ==========

    def _get_emotion_response(self, text: str) -> str:
        """情感回应"""
        if "开心" in text or "高兴" in text:
            return "很高兴您心情不错！有什么需要我帮忙的吗？"
        if "谢谢" in text or "感谢" in text:
            return "不客气！很高兴能帮到您。"
        if "难过" in text or "伤心" in text:
            return "很抱歉听到这个消息...希望您能好起来。"
        return None

    def _extract_name(self, text: str) -> str:
        match = re.search(r'我叫([\u4e00-\u9fa5]{2,4})', text)
        if match:
            name = match.group(1)
            if name not in ["什么", "哪个", "谁", "啥"]:
                return name
        return None

    def _get_conversation_context(self, user_input: str) -> str:
        if not self._conversation_history:
            return user_input
        context_parts = ["【对话历史】"]
        for msg in self._conversation_history[-self._max_history:]:
            context_parts.append(f"用户: {msg['user']}")
            context_parts.append(f"助手: {msg['assistant']}")
        context_parts.append(f"\n【当前】{user_input}")
        return "\n".join(context_parts)

    def _update_conversation(self, user_input: str, response: str):
        self._conversation_history.append({
            "user": user_input[:200],
            "assistant": response[:200],
            "timestamp": datetime.now().isoformat()
        })
        if len(self._conversation_history) > self._max_history:
            self._conversation_history = self._conversation_history[-self._max_history:]

    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }



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
    
   
    def _rule_based_decompose(self, task: str) -> Dict:
        """基于规则的任务分解"""
        parts = re.split(r'然后|接着|之后|再', task)
        sub_tasks = []
        for i, part in enumerate(parts, 1):
            part = part.strip()
            if not part:
                continue
            sub_tasks.append({
                "id": i,
                "action": "process",
                "target": "task",
                "description": part,
                "depends_on": [i-1] if i > 1 else []
            })
        return {"sub_tasks": sub_tasks, "mode": "sequential" if len(sub_tasks) > 1 else "simple"}    
    




if __name__ == "__main__":
    agent = ButlerAgentV4("test")
    print("\n✅ ButlerAgentV4 测试通过")


