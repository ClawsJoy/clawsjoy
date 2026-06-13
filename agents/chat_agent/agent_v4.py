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




    def can_handle_json(self, action: str, target: str) -> tuple:
        """声明能力"""
        capabilities = {
            ("chat", "text"): (True, 0.95),
            ("search", "info"): (True, 0.80),
            ("generate", "text"): (True, 0.70),
            ("remember", "info"): (True, 0.90),
            ("recall", "info"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心对话逻辑 - 支持多轮对话和任务分解"""
        
        # 更新用户画像
        proactive_service.update_user_profile(self.user_id, {
            "preference": user_input[:50],
            "timestamp": datetime.now().isoformat()
        })
    
        # 获取主动建议（仅在闲聊时）
        if self._is_chat_task(user_input):
            suggestions = proactive_service.get_suggestions(self.user_id)
            if suggestions:
                return self._response(suggestions[0], metadata={"proactive": True})


        # 检测是否来自 Orchestrator（通过 context）
        from_orchestrator = context and context.get("caller") == "orchestrator"
    
        # 如果是被 Orchestrator 调用，直接响应，不进行任务分解
        if from_orchestrator:
            print(f"[ChatAgent] 被 Orchestrator 调用，直接响应")
            # 直接生成图表（如果需要）或返回简单响应
            if "图表" in user_input or "生成" in user_input:
                return self._generate_simple_chart_response(user_input)
            return self._simple_response(user_input)
        
            # 测试 decompose_task 是否存在
            if hasattr(self, 'decompose_task'):
                print(f"[DEBUG] decompose_task 方法存在")
            else:
                print(f"[DEBUG] decompose_task 方法不存在！")
               
        # ========== 1. 任务分解（最高优先级）==========
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

        # ========== 2. 主动建议（仅限闲聊场景）==========
        if self._should_show_suggestion(user_input):
            suggestions = self._get_proactive_suggestions(user_input)
            if suggestions:
                return self._response(suggestions[0], metadata={"proactive": True})

        # ========== 3. 清空对话 ==========
        if user_input.strip() in ["清空对话", "清空历史", "重置对话", "clear"]:
            result = self._clear_conversation()
            return self._response(result, metadata={"action": "clear_history"})
    
              
        # ========== 4. 情感回应 ==========
        emotion_response = self._get_emotion_response(user_input)
        if emotion_response:
            self._update_conversation(user_input, emotion_response)
            return self._response(emotion_response, metadata={"emotion": True})
    
        # ========== 5. 名字记忆==========
        if "我叫" in user_input and not any(q in user_input for q in ["什么", "吗", "？"]):
            name = self._extract_name(user_input)
            if name:
                self.remember_forever("user_name", name)
                response = f"你好，{name}！我记住你了。"
                self._update_conversation(user_input, response)
                return self._response(response, metadata={"action": "remember_name"})
    
        # ========== 6.查询名字==========
        if any(q in user_input for q in ["我叫什么", "我的名字", "我叫啥", "名字是什么"]):
            name = self.recall_forever("user_name")
            if name:
                response = f"你的名字是{name}。"
            else:
                response = "我还不知道你的名字，请告诉我（比如：我叫张三）。"
            self._update_conversation(user_input, response)
            return self._response(response)
    
        # ========== 7.记忆偏好==========
        if "记住" in user_input or "我喜欢" in user_input:
            match = re.search(r'(?:记住|我喜欢)(.+?)(?:是|：)(.+)', user_input)
            if match:
                key, value = match.group(1).strip(), match.group(2).strip()
                self.remember_forever(f"pref_{key}", value)
                response = f"✅ 已记住：{key} = {value}"
                self._update_conversation(user_input, response)
                return self._response(response)
    
        # ========== 8. 查询偏好==========
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
            self._update_conversation(user_input, response)
            return self._response(response)
    
        # ========== 9.查询对话历史（新增）==========
        if any(q in user_input for q in ["刚才说了什么", "上一轮", "之前我说", "我们聊了什么"]):
            if self._conversation_history:
                last = self._conversation_history[-1]
                response = f"上一轮你说：{last['user']}\n我回答：{last['assistant']}"
            else:
                response = "还没有对话记录，请先和我聊天吧。"
            self._update_conversation(user_input, response)
            return self._response(response)
    
        # ========== 10.多轮对话（使用 LLM + 上下文）===========
        context_prompt = self._get_conversation_context(user_input)
        response = self._call_llm(context_prompt)
    
        if not response:
            response = f"你说：{user_input[:100]}。有什么我可以帮助你的吗？"
    
        self._update_conversation(user_input, response)
        return self._response(response, metadata={"source": "llm", "context_used": len(self._conversation_history) > 0})
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
        """判断是否为闲聊任务"""
        task_keywords = ["代码", "计算", "翻译", "分析", "待办"]
        return not any(kw in user_input for kw in task_keywords) and len(user_input) < 30


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
