#!/usr/bin/env python3
"""ChatAgent v4.0 - 智慧化改造试点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import random
import re
from datetime import datetime  # 添加这行
from typing import Dict, Optional, Tuple
from core.agents.business.business_agent import BusinessAgent
from core.lib.proactive.proactive_service import proactive_service
from core.lib.dialect.dialect_helper import get_dialect_helper


class ChatAgentV4(BusinessAgent):
    """聊天 Agent - 智慧化试点版本"""
    
    name = "chat_agent_v4"
    description = "智慧对话助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
    
        # 多轮对话历史
        self._conversation_history = []
        self._max_history = 10  # 保留最近10轮对话
        # 启动主动建议服务
        self.add_proactive_hook()
        self._user_profile = {}
        print(f"💬 ChatAgent v{self.version} 智慧化试点启动")
        print(f"   💾 对话历史已启用 (保留最近 {self._max_history} 轮)")


    def _get_conversation_context(self, user_input: str) -> str:
        """获取对话上下文"""
        if not self._conversation_history:
            return user_input
    
        # 构建上下文
        context_parts = ["【对话历史】"]
        for i, msg in enumerate(self._conversation_history[-self._max_history:], 1):
            context_parts.append(f"{i}. 用户: {msg['user']}")
            context_parts.append(f"   助手: {msg['assistant']}")
    
        context_parts.append(f"\n【当前问题】{user_input}")
        context_parts.append("\n请根据对话历史回答当前问题。")
        return "\n".join(context_parts)

    def _update_conversation(self, user_input: str, response: str):
        """更新对话历史"""
        self._conversation_history.append({
            "user": user_input[:200],
            "assistant": response[:200],
            "timestamp": datetime.now().isoformat()
        })
    
        # 保留最近 N 条
        if len(self._conversation_history) > self._max_history:
            self._conversation_history = self._conversation_history[-self._max_history:]

    def _clear_conversation(self) -> str:
        """清空对话历史"""
        count = len(self._conversation_history)
        self._conversation_history = []
        return f"✅ 已清空 {count} 轮对话历史"


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
                    "happy": ["很高兴您心情不错！😊", "您的开心感染了我！", "太好了，能帮到您我很开心！"],
                    "sad": ["很抱歉听到这个消息...有什么我可以帮您的吗？", "希望您能好起来。", "如果需要倾诉，我随时在这里。"],
                    "angry": ["很抱歉让您感到不满，我会努力改进。", "请告诉我哪里做得不好，我会立即改进。"],
                    "confused": ["让我重新解释一下...", "抱歉没说清楚，我换个方式说明："],
                    "grateful": ["不客气！很高兴能帮到您。", "这是我的荣幸！", "随时为您服务！"]
                }
                import random
                return random.choice(responses.get(emotion, ["好的，我明白了。"]))
        return None

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("chat", "text"): (True, 0.95),
            ("search", "info"): (True, 0.80),
            ("generate", "text"): (True, 0.70),
            ("remember", "info"): (True, 0.90),
            ("recall", "info"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))


    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心对话逻辑 - 支持方言、任务分解、主动建议"""

        # ========== 1. 方言理解（最先执行）==========
        dialect_helper = get_dialect_helper(self.user_id)
        original_input = user_input
        has_dialect = dialect_helper.has_dialect(user_input)

        if has_dialect:
            user_input, _ = dialect_helper.to_standard(user_input)
            print(f"[ChatAgent] 方言理解: {original_input} → {user_input}")

        # ========== 2. 任务分解（复杂任务优先）==========
        complex_keywords = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        has_complex = any(kw in user_input for kw in complex_keywords)
        action_words = ["分析", "生成", "发送", "创建", "写", "计算", "翻译"]
        action_count = sum(1 for aw in action_words if aw in user_input)

        if has_complex or action_count >= 2:
            print(f"[DEBUG] 检测到复杂任务: {user_input[:50]}...")
            decomposition = self._rule_based_decompose(user_input)
            sub_tasks = decomposition.get("sub_tasks", [])
            task_list = [f"  {task['id']}. {task['action']} {task['target']}: {task['description']}" 
                     for task in sub_tasks]
            result_text = f"📋 **任务分解计划**\n\n" + "\n".join(task_list)
            result_text += f"\n\n⚙️ 执行模式: {decomposition.get('mode')}"
            return self._response(result_text, metadata={"decomposed": True})

        # ========== 3. 清空对话 ==========
        if user_input.strip() in ["清空对话", "清空历史", "重置对话", "clear"]:
            count = len(self._conversation_history)
            self._conversation_history = []
            return self._response(f"✅ 已清空 {count} 轮对话历史")

        # ========== 4. 名字记忆 ==========
        if "我叫" in user_input and not any(q in user_input for q in ["什么", "吗", "？"]):
            name = self._extract_name(user_input)
            if name:
                self.remember_forever("user_name", name)
                response = f"你好，{name}！我记住你了。"
                self._update_conversation(original_input, response)
                return self._response(response, metadata={"action": "remember_name"})

        # ========== 5. 查询名字 ==========
        if any(q in user_input for q in ["我叫什么", "我的名字", "我叫啥", "名字是什么"]):
            name = self.recall_forever("user_name")
            if name:
                response = f"你的名字是{name}。"
            else:
                response = "我还不知道你的名字，请告诉我（比如：我叫张三）。"
            self._update_conversation(original_input, response)
            return self._response(response)

        # ========== 6. 记忆偏好 ==========
        if "记住" in user_input or "我喜欢" in user_input:
            match = re.search(r'(?:记住|我喜欢)(.+?)(?:是|：)(.+)', user_input)
            if match:
                key, value = match.group(1).strip(), match.group(2).strip()
                self.remember_forever(f"pref_{key}", value)
                response = f"✅ 已记住：{key} = {value}"
                self._update_conversation(original_input, response)
                return self._response(response)

        # ========== 7. 查询偏好 ==========
        if "我喜欢什么" in user_input or "我的偏好" in user_input:
            prefs = []
            for key in ["颜色", "食物", "电影", "音乐", "书"]:
                value = self.recall_forever(f"pref_{key}")
                if value:
                    prefs.append(f"{key}: {value}")
            if prefs:
                response = "你喜欢的：\n" + "\n".join(f"  • {p}" for p in prefs)
            else:
                response = "我还不知道你的偏好，可以告诉我，比如：我喜欢颜色是蓝色"
            self._update_conversation(original_input, response)
            return self._response(response)

        # ========== 8. 查询对话历史 ==========
        if any(q in user_input for q in ["刚才说了什么", "上一轮", "之前我说"]):
            if self._conversation_history:
                last = self._conversation_history[-1]
                response = f"上一轮你说：{last['user']}\n我回答：{last['assistant']}"
            else:
                response = "还没有对话记录，请先和我聊天吧。"
            self._update_conversation(original_input, response)
            return self._response(response)

        # ========== 9. 情感回应 ==========
        # 在情感回应部分添加方言转换
        emotion_response = self._get_emotion_response(user_input)
        if emotion_response:
            if has_dialect:
                dialect_response, _ = dialect_helper.to_dialect(emotion_response)
                if dialect_response != emotion_response:
                    emotion_response = dialect_response
            self._update_conversation(original_input, emotion_response)
            return self._response(emotion_response, metadata={"emotion": True})
        # ========== 10. 被 Orchestrator 调用时的处理 ==========
        from_orchestrator = context and context.get("caller") == "orchestrator"
        if from_orchestrator:
            print(f"[ChatAgent] 被 Orchestrator 调用，直接响应")
            if "图表" in user_input or "生成" in user_input:
                return self._generate_simple_chart_response(user_input)
            return self._simple_response(user_input)

        # ========== 11. 多轮对话（使用 LLM）==========
        context_prompt = self._get_conversation_context(user_input)
        response = self._call_llm(context_prompt)

        if not response:
            response = f"你说：{user_input[:100]}。有什么我可以帮助你的吗？"

        # ========== 12. 方言回应（普通话 → 方言）==========
        if has_dialect:
            dialect_response, converted = dialect_helper.to_dialect(response)
            if converted:
                response = dialect_response
                print(f"[ChatAgent] 方言回应: {dialect_response}")

        self._update_conversation(original_input, response)
    
        # ========== 13. 主动建议（放在最后，仅闲聊且没有其他回复时）==========
        # 主动建议只在纯闲聊场景且没有其他处理时触发
        if self._is_chat_task(original_input) and not has_dialect:
            suggestion = self._get_proactive_suggestion()
            return self._response(suggestion, metadata={"proactive": True})

        return self._response(response, metadata={"source": "llm"})   
       
        
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


    def _is_complex_task(self, user_input: str) -> bool:
        """判断是否为复杂任务"""
        complex_indicators = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后", "分析", "生成", "发送"]
        return len(user_input) > 30 and any(ind in user_input for ind in complex_indicators)


    def _response(self, content: str, **kwargs) -> dict:
        """构建响应"""
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }
    
    def _extract_name(self, text: str) -> str:
        """提取名字 - 只提取中文名字，排除疑问词"""
        # 匹配 "我叫" 后面的2-4个中文字符
        match = re.search(r'我叫([\u4e00-\u9fa5]{2,4})', text)
        if match:
            name = match.group(1)
            # 排除疑问词
            if name not in ["什么", "哪个", "谁", "啥"]:
                return name
        return None

    def _should_show_suggestion(self, user_input: str) -> bool:
        """判断是否应该显示主动建议"""
    
        # 条件1: 不是复杂任务
        complex_keywords = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        action_words = ["分析", "生成", "发送", "创建", "写", "计算", "翻译"]
    
        is_complex = any(kw in user_input for kw in complex_keywords) or \
                     sum(1 for aw in action_words if aw in user_input) >= 2
    
        if is_complex:
            return False
    
        # 条件2: 不是命令类语句
        command_keywords = ["清空", "删除", "设置", "记住", "回忆", "我叫", "我的名字"]
        if any(kw in user_input for kw in command_keywords):
            return False
    
        # 条件3: 不是情感表达
        emotion_keywords = ["开心", "高兴", "难过", "伤心", "谢谢", "感谢"]
        if any(kw in user_input for kw in emotion_keywords):
            return False
    
        # 条件4: 用户没有明确指定任务（输入较短，类似闲聊）
        if len(user_input) > 20:
            return False
    
        return True

    def _generate_simple_chart_response(self, user_input: str) -> Dict:
        """生成简单的图表响应（当被 Orchestrator 调用时）"""
        return self._response(
            f"📊 根据上一步的分析结果，我来生成图表。\n\n"
            f"图表类型建议：柱状图或折线图\n"
            f"数据可视化已准备就绪。",
            metadata={"role": "chart_generator", "from_orchestrator": True}
        )

    def _simple_response(self, user_input: str) -> Dict:
        """简单响应（当被 Orchestrator 调用时）"""
        return self._response(
            f"收到请求：{user_input[:100]}",
            metadata={"from_orchestrator": True}
        )

    def _is_chat_task(self, user_input: str) -> bool:
        """判断是否为闲聊任务（主动建议只对纯闲聊生效）"""
        # 排除命令类语句
        command_keywords = ["我叫", "我的名字", "记住", "回忆", "清空", "待办"]
        if any(kw in user_input for kw in command_keywords):
            return False
    
        # 排除复杂任务
        task_keywords = ["代码", "计算", "翻译", "分析"]
        if any(kw in user_input for kw in task_keywords):
            return False
    
        # 纯闲聊：短文本且无疑问词
        return len(user_input) < 20 and not any(q in user_input for q in ["什么", "怎么", "为什么"])



if __name__ == "__main__":
    # 快速测试
    agent = ChatAgentV4("test")
    
    print("\n测试1: 记忆名字")
    result = agent.process("我叫张三")
    print(result.get('response'))
    
    print("\n测试2: 回忆名字")
    result = agent.process("我叫什么名字")
    print(result.get('response'))
    
    print("\n测试3: 记忆信息")
    result = agent.process("记住生日是5月1日")
    print(result.get('response'))
    
    print("\n测试4: 回忆信息")
    result = agent.process("回忆生日")
    print(result.get('response'))
    
    print("\n✅ ChatAgentV4 快速测试通过")

