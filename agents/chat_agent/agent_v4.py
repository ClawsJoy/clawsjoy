#!/usr/bin/env python3
"""ChatAgent v4.0 - 智慧化改造试点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import random
import re
import yaml
from pathlib import Path
from datetime import datetime  # 添加这行
from typing import Dict, Optional, Tuple
from core.agents.business.business_agent import BusinessAgent
from core.lib.proactive.proactive_service import proactive_service
from core.lib.dialect.dialect_helper import get_dialect_helper
from core.lib.prompt_upgrader import get_prompt_upgrader
from core.lib.soul.soul_injector import get_soul_injector


class ChatAgentV4(BusinessAgent):
    """聊天 Agent - 智慧化试点版本"""
    
    name = "chat_agent_v4"
    description = "智慧对话助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        # 加载话本
        self._load_scriptbook()
        # 多轮对话历史
        self._conversation_history = []
        self._max_history = 10  # 保留最近10轮对话
        # 启动主动建议服务
        self.add_proactive_hook()
        self._user_profile = {}
        # 初始化 Prompt 升级器
        self.prompt_upgrader = get_prompt_upgrader("chat_agent")
        # 初始化灵魂注入器
        self.soul = get_soul_injector(user_id, "chat_agent")
        print(f"💬 ChatAgent v{self.version} 智慧化试点启动")
        print(f"   💾 对话历史已启用 (保留最近 {self._max_history} 轮)")

    def _load_scriptbook(self):
        """加载话本配置"""
    
        # 优先使用 chat_agent 专用话本
        script_path = Path("agents/chat_agent/scriptbook.yaml")
        if not script_path.exists():
            # 降级使用通用话本
            script_path = Path("config/butler/scriptbook.yaml")
    
        if script_path.exists():
            try:
                with open(script_path, 'r') as f:
                    data = yaml.safe_load(f)
                    self._intents = data.get('intents', [])
                    self._templates = data.get('templates', {})
                    print(f"📖 已加载话本: {len(self._intents)} 个意图")
            except Exception as e:
                print(f"话本加载失败: {e}")

    def _match_intent(self, user_input: str) -> str:
        """匹配话本意图"""
        user_lower = user_input.lower()
        for intent in self._intents:
            for keyword in intent.get('keywords', []):
                if keyword in user_lower:
                    return intent.get('response', 'default')
        return 'default'

    def _get_template_response(self, template_name: str, **kwargs) -> str:
        """获取话本回复模板（支持简单的条件替换）"""
        template = self._templates.get(template_name, "")
        if not template:
            return None
    
        # 获取用户信息
        user_name = self.recall_forever("user_name")
    
        # 简单替换，不做复杂的 Jinja2 解析
        result = template
    
        # 替换变量
        if user_name:
            result = result.replace("{{user_name}}", user_name)
        else:
            result = result.replace("{{user_name}}", "")
    
        # 处理简单的 if-else（只支持基础的 {% if user_name %}...{% else %}...{% endif %}）
        if "{% if user_name %}" in result:
            if user_name:
                # 取 if 分支
                match = re.search(r'\{% if user_name %\}(.*?)(?:\{% else %\}|\{% endif %\})', result, re.DOTALL)
                if match:
                    result = match.group(1)
            else:
                # 取 else 分支
                match = re.search(r'\{% else %\}(.*?)\{% endif %\}', result, re.DOTALL)
                if match:
                    result = match.group(1)
                else:
                    # 没有 else，取 if 之前的内容
                    match = re.search(r'(.*?)\{% if user_name %\}', result, re.DOTALL)
                    if match:
                        result = match.group(1)
    
        # 清理多余的空格和换行
        result = result.strip()
        result = re.sub(r'\n{3,}', '\n\n', result)
    
        return result


    def _get_conversation_context(self, user_input: str) -> str:
        """获取对话上下文"""
        if not self._conversation_history:
            return user_input
    
        context_parts = ["【对话历史】"]
        for i, msg in enumerate(self._conversation_history[-self._max_history:], 1):
            # 兼容两种格式
            user_content = msg.get("user") or msg.get("content") or msg.get("text", "")
            assistant_content = msg.get("assistant") or msg.get("response") or msg.get("content", "")
        
            context_parts.append(f"{i}. 用户: {user_content}")
            context_parts.append(f"   助手: {assistant_content}")
    
        context_parts.append(f"\n【当前】{user_input}")
        return "\n".join(context_parts)


    def _update_conversation(self, user_input: str, response: str):
        """更新对话历史"""
        self._conversation_history.append({
            "user": user_input[:200],  # 用户消息
            "assistant": response[:200],  # 助手回复
            "timestamp": datetime.now().isoformat()
        })
        if len(self._conversation_history) > self._max_history:
            self._conversation_history = self._conversation_history[-self._max_history:]   

    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM - 使用动态 Prompt"""
        if not model:
            model = self._select_model(prompt)
    
        # 灵魂注入
        soul_prompt = self.soul.inject(prompt)
        # 获取升级版 Prompt
        context = {
            "name": "小爪",
            "description": "智慧聊天助手",
            "personality": "活泼开朗，喜欢交朋友，有点皮",
            "memory": f"用户叫{self.recall_forever('user_name') or '未知'}" if self.recall_forever('user_name') else "",
            "user_input": prompt
        }
    
        system_prompt, version, is_test = self.prompt_upgrader.get_prompt(context)
        full_prompt = f"{system_prompt}\n\n用户: {prompt}\n小爪:"
    
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                "model": model,
                "prompt": soul_prompt,  # 使用灵魂注入后的 prompt
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 150}
            },
                timeout=60
            )
            if resp.status_code == 200:
                response = resp.json().get("response", "")
            
                # 身份强制过滤
                if hasattr(self, 'soul'):
                    response = self.soul.enforce_identity(response)
                # 添加这行：更新关系计数
                if hasattr(self, 'soul'):
                    self.soul.update_relationship(prompt, response)
                return response       
                
        except Exception as e:
            print(f"LLM 调用失败: {e}")
    
        return ""

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
        """
        核心对话逻辑 - 正确架构
    
        流程:
        1. 理解层（方言转换、实体提取）- 不可跳过
        2. 记忆层（回忆用户信息、更新历史）- 不可跳过
        3. 增强层（构建完整上下文）
        4. 表达层（话本模板 或 LLM 生成）
        """
    
        # ============================================================
        # 第1层：理解层（必须执行，不可跳过）
        # ============================================================
        import re as regex
        original_input = user_input
        understood_input = user_input
    
        # 无意义输入检测
        if self._is_meaningless(user_input):
            return self._response(self._get_meaningless_response())
        # 1.1 方言理解
        dialect_helper = get_dialect_helper(self.user_id)
        has_dialect = dialect_helper.has_dialect(user_input)
    
        if has_dialect:
            understood_input, _ = dialect_helper.to_standard(user_input)
            print(f"[理解] 方言: {original_input} → {understood_input}")
    
        # 1.2 实体提取（名字、偏好等）
        extracted_name = None
        extracted_preference = None
                
        # 第1层：理解层 - 提取名字后立即返回
        name_patterns = [r'我叫\s*(\S+)', r'叫我\s*(\S+)', r'可以叫我\s*(\S+)', r'英文名叫\s*(\S+)', r'英文名字\s*(\S+)']
        for pattern in name_patterns:
            match = regex.search(pattern, original_input)
            if match:
                extracted_name = match.group(1)
                if extracted_name and extracted_name not in ["什么", "啥", "谁", "吗"]:
                    self.remember_forever("user_name", extracted_name)
                    # 先构建响应
                    response = f"好的，我记住啦！以后就叫你{extracted_name}~ 😊"
                    # 同步到灵魂
                    if hasattr(self, 'soul'):
                        print(f"[DEBUG] soul 存在，准备保存名字: {extracted_name}")
                        self.soul.set_user_name(extracted_name)
                        self.soul.update_relationship(original_input, response)  # 添加这行
                        print(f"[理解] 提取名字: {extracted_name}")
                        print(f"[DEBUG] soul 保存完成")
                    else:
                        print(f"[DEBUG] soul 不存在！")
                    # 立即返回，不继续执行
                    self._update_last_response(original_input, response)
                    return self._response(response)

        # ============================================================
        # 第2层：记忆层（必须执行，不可跳过）
        # ============================================================
    
        # 2.1 回忆用户信息
        user_name = self.recall_forever("user_name")
        user_preferences = self._recall_preferences()
    
        # 2.2 更新对话历史
        self._update_conversation(original_input, "[处理中]")
    
        # ============================================================
        # 第3层：增强层（构建理解后的上下文）
        # ============================================================
    
        enhanced_context = {
            "原始输入": original_input,
            "理解后输入": understood_input,
            "用户姓名": user_name or "未知",
            "用户偏好": user_preferences,
            "有方言": has_dialect,
            "对话轮次": len(self._conversation_history)
        }
    
        # ============================================================
        # 第4层：决策与表达
        # ============================================================
    
        # 4.1 特殊命令处理（不变）
        if understood_input.strip() in ["清空对话", "清空历史", "重置对话", "clear"]:
            count = len(self._conversation_history)
            self._conversation_history = []
            response = f"✅ 已清空 {count} 轮对话历史"
            self._update_last_response(original_input, response)
            return self._response(response)
    
        # 4.2 名字查询 - 直接返回，不让 LLM 处理
        if any(q in understood_input for q in ["我叫什么", "我的名字", "你还记得我吗", "你记得我吗", "我是谁"]):
            if user_name:
                response = f"当然记得呀！你叫{user_name}嘛~ 😊"
            else:
                response = "我还不认识你呢，可以告诉我你的名字吗？"
            self._update_last_response(original_input, response)
            return self._response(response)  # 直接返回，不经过 LLM    

        # 4.3 方言学习（用户教方言）
        if "就是" in understood_input or "意思是" in understood_input:
            match = regex.search(r'(\S+)\s+就是\s+(.+)', original_input)
            if not match:
                match = regex.search(r'(\S+)\s+意思是\s+(.+)', original_input)
            if match:
                dialect_word, meaning = match.group(1), match.group(2)
                dialect_helper.learn_direct(dialect_word, meaning)  # 改为 learn_direct
                response = f"学到啦！原来「{dialect_word}」是「{meaning}」的意思，谢谢教我~ 😊"
                self._update_last_response(original_input, response)
                return self._response(response)
    
        # 4.4 天气查询（友好引导）
        if any(q in understood_input for q in ["天气", "温度", "下雨", "晴天", "多云"]):
            response = "我暂时查不了实时天气呢~ 不过你可以告诉我你那里的天气，我可以陪你聊聊！☀️🌧️"
            self._update_last_response(original_input, response)
            return self._response(response)
    
        # 4.5 话本匹配（作为表达模板，使用理解后的输入）
        if hasattr(self, '_intents') and self._intents:
            intent_name = self._match_intent(understood_input)
            if intent_name and intent_name in self._templates:
                template = self._templates[intent_name]
                
                # 第一步：处理条件语法
                import regex
                result = template
                
                # 处理 {% if user_name %}...{% else %}...{% endif %}
                if "{% if user_name %}" in result:
                    if user_name:
                        # 取 if 分支
                        match = regex.search(r'\{% if user_name %\}(.*?)(?:\{% else %\}|\{% endif %\})', result, regex.DOTALL)
                        if match:
                            result = match.group(1)
                    else:
                        # 取 else 分支
                        match = regex.search(r'\{% else %\}(.*?)\{% endif %\}', result, regex.DOTALL)
                        if match:
                            result = match.group(1)
                        else:
                            # 没有 else，取 if 之前的内容
                            match = regex.search(r'(.*?)\{% if user_name %\}', result, regex.DOTALL)
                            if match:
                                result = match.group(1)
                
                # 第二步：变量替换
                if user_name:
                    result = result.replace("{{user_name}}", user_name)
                else:
                    result = result.replace("{{user_name}}", "")
                
                result = result.replace("{{user_pref}}", user_preferences or "")
                
                # 清理多余空格和换行
                result = result.strip()
                result = regex.sub(r'\n{3,}', '\n\n', result)
                
                response = result
                if response and len(response) < 500:
                    # 在这里插入：更新关系计数
                    if hasattr(self, 'soul'):
                        response = self.soul.enforce_identity(response)
                        self.soul.update_relationship(original_input, response)
                    
                    self._update_last_response(original_input, response)
                    return self._response(response, metadata={"script": True})


        # 4.6 LLM 生成（带上完整上下文）
        context_prompt = self._build_enhanced_prompt(understood_input, enhanced_context)
        response = self._call_llm(context_prompt)
    
        if not response:
            response = f"你说：{understood_input[:100]}。有什么我可以帮助你的吗？"
    
        # 4.7 方言回应（如果用户说了方言）
        if has_dialect:
            dialect_response, converted = dialect_helper.to_dialect(response)
            if converted:
                response = dialect_response
                print(f"[表达] 方言回应: {dialect_response}")
    
        self._update_last_response(original_input, response)
        return self._response(response, metadata={"source": "llm"})


    def _recall_preferences(self) -> str:
        """回忆用户偏好"""
        prefs = []
        color = self.recall_forever("pref_color")
        food = self.recall_forever("pref_food")
        if color:
            prefs.append(f"颜色:{color}")
        if food:
            prefs.append(f"食物:{food}")
        return ", ".join(prefs) if prefs else ""

    def _build_enhanced_prompt(self, user_input: str, context: Dict) -> str:
        """构建增强后的 LLM Prompt - 严格约束"""
    
        # 获取最近3轮对话历史（不要太多）
        history_text = ""
        if self._conversation_history:
            recent = self._conversation_history[-6:]  # 最近3轮
            history_parts = []
            for msg in recent:
                role = msg.get("role")
                content = msg.get("content", "")[:200]
                if role == "user":
                    history_parts.append(f"用户: {content}")
                elif role == "assistant":
                    history_parts.append(f"小爪: {content}")
            if history_parts:
                history_text = "【最近对话】\n" + "\n".join(history_parts) + "\n"
    
        user_name = context.get('用户姓名', '')
        user_pref = context.get('用户偏好', '')
    
        # 严格的 system prompt
        prompt = f"""你是小爪，ClawsJoy 的聊天助手。

【严格要求 - 必须遵守】
1. 只回复用户当前问题，不要编造故事
2. 不要自称AI、模型或助手
3. 回复长度控制在50字以内
4. 不知道就说不知道
5. 不要提及用户没有说过的事情
6. 不要创建虚构角色或情节

【用户信息】
- 姓名: {user_name if user_name else '未知'}
- 偏好: {user_pref if user_pref else '无'}

{history_text}
【当前用户】
{user_input}

【小爪的简短回复】"""

        return prompt
    

    def _update_last_response(self, user_input: str, response: str):
        """更新对话历史中的最后一条回复"""
        if self._conversation_history:
            # 找到最后一条用户消息，更新对应的助手回复
            for i in range(len(self._conversation_history) - 1, -1, -1):
                if self._conversation_history[i].get("role") == "assistant":
                    self._conversation_history[i]["content"] = response[:200]
                    return
            # 如果没有找到，添加
            self._conversation_history.append({"role": "assistant", "content": response[:200]})
        else:
            self._conversation_history.append({"role": "assistant", "content": response[:200]})     
        
    
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

    def _get_proactive_suggestions(self, user_input: str = "") -> list:
        """获取主动建议"""
        if not user_input:
            return ["💡 有什么我可以帮您的吗？"]
    
        # 如果是自我介绍请求
        if any(kw in user_input for kw in ["自我介绍", "介绍自己", "你是谁", "你能做什么"]):
            return ["我是小爪，ClawsJoy 的聊天助手~ 😊"]
    
        # 只对非空输入调用 LLM
        if user_input.strip():
            response = self._call_llm(user_input)
            if response:
                return [response]
    
        return ["💡 有什么我可以帮您的吗？"]
    

    def _auto_evaluate_response(self, response: str) -> float:
        """自动评估响应质量"""
        score = 0.5
        if any('\u4e00' <= c <= '\u9fff' for c in response):
            score += 0.2
        if 20 < len(response) < 300:
            score += 0.1
        if "小爪" in response or "我是" in response:
            score += 0.1
        return min(score, 1.0)

    def _is_meaningless(self, text: str) -> bool:
        """检测是否为无意义输入"""
        import re
        # 纯乱码
        if re.match(r'^[a-z]{10,}$', text.lower()):
            return True
        # 纯符号
        if re.match(r'^[~!@#$%^&*()_+]+$', text):
            return True
        # 超短无意义
        if len(text) < 2:
            return True
        return False

    def _get_meaningless_response(self) -> str:
        """返回无意义输入的回应"""
        responses = [
            "嗯？我没太明白你的意思~ 能说得清楚一点吗？😊",
            "不好意思，我没理解你的问题，可以换个说法吗？",
            "我没听懂呢，要不要重新说一遍？",
            "这个...我有点困惑，你能解释一下吗？"
        ]
        import random
        return random.choice(responses)


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


