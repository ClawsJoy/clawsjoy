#!/usr/bin/env python3
"""统一对话引擎 - 完整版（含持久化记忆）"""

import requests
from core.lib.vector_knowledge_center import vector_knowledge_center
from core.lib.unified_config import unified_config
import logging
import re
import json
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Union, Dict, List, Optional
logger = logging.getLogger(__name__)


class PersistentMemory:
    """内嵌持久化记忆"""
    
    def __init__(self, storage_dir="data/memories"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def get_user_info(self, user_id: str) -> Dict:
        """获取用户信息"""
        user_file = self.storage_dir / f"{user_id}.json"
        if user_file.exists():
            try:
                with open(user_file, 'r') as f:
                    data = json.load(f)
                    return {
                        'name': data.get('name', ''),
                        'preferences': data.get('preferences', [])
                    }
            except:
                pass
        return {'name': '', 'preferences': []}
           
    def load_context(self, user_id: str, last_n: int = 5) -> str:
        """加载最近的对话上下文"""
        user_file = self.storage_dir / f"{user_id}.json"
        if not user_file.exists():
            return ""
        
        try:
            with open(user_file, 'r') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            if not conversations:
                return ""
            
            context = "【历史对话】\n"
            for conv in conversations[-last_n:]:
                context += f"用户: {conv.get('user', '')}\n"
                context += f"助手: {conv.get('assistant', '')}\n"
            
            return context
        except:
            return ""      
    

    def save_conversation(self, user_id: str, user_msg: str, assistant_msg: str):
        """保存对话记录"""
        user_file = self.storage_dir / f"{user_id}.json"
        data = {}
        if user_file.exists():
            try:
                with open(user_file, 'r') as f:
                    data = json.load(f)
            except:
                pass
        
        if 'conversations' not in data:
            data['conversations'] = []
        
        data['conversations'].append({
            'user': user_msg[:200],
            'assistant': assistant_msg[:200],
            'timestamp': datetime.now().isoformat()
        })
        
        # 只保留最近50条
        if len(data['conversations']) > 50:
            data['conversations'] = data['conversations'][-50:]
        
        with open(user_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

class UnifiedChatEngine:

    def _get_agent_instance(self, agent_name: str):
        """动态获取 Agent 实例"""
        try:
            import importlib
            module_path = f"agents.{agent_name}.agent"
            module = importlib.import_module(module_path)
            
            # 尝试获取预定义的实例
            if hasattr(module, agent_name):
                return getattr(module, agent_name)
            
            # 查找 Agent 类并实例化
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, 'name') and getattr(attr, 'name') == agent_name:
                    return attr()
        except Exception as e:
            logger.error(f"获取 Agent {agent_name} 失败: {e}")
        return None

    def __init__(self):
        self.llm_url = "http://localhost:11434/api/generate"
        self.llm_model = "qwen2:1.5b-instruct"
        self.timeout = 30
        self.max_retries = 2
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        self.user_profiles: Dict[str, Dict] = defaultdict(dict)
        self._cache = {}
        self._cache_ttl = 300
        
        # 持久化记忆
        self.persistent_memory = PersistentMemory()
        
        logger.info("✅ ChatEngine 初始化完成（含持久化记忆）")

    def _cache_get(self, key: str):
        import time
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
            else:
                del self._cache[key]
        return None

    
    def _extract_user_info(self, user_id: str, message: str):
        """从消息中提取用户信息"""
        profile = self.user_profiles.get(user_id, {})
        
        # 提取名字
        import re
        name_match = re.search(r'我叫([^，,。]+)', message)
        if name_match:
            profile['name'] = name_match.group(1).strip()
        
        # 提取偏好
        pref_match = re.search(r'我喜欢([^，,。]+)', message)
        if pref_match:
            if 'preferences' not in profile:
                profile['preferences'] = []
            profile['preferences'].append(pref_match.group(1).strip())
        
        self.user_profiles[user_id] = profile

    def _cache_set(self, key: str, value: str):
        import time
        self._cache[key] = (value, time.time())
        if len(self._cache) > 500:
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest]

    def _load_persistent_memory(self, user_id: str):
        """从持久化存储加载用户信息"""
        user_info = self.persistent_memory.get_user_info(user_id)
        if user_info.get('name'):
            self.user_profiles[user_id]['name'] = user_info['name']
        if user_info.get('preferences'):
            self.user_profiles[user_id]['preferences'] = user_info['preferences']
        
        # 加载历史对话到当前会话
        context = self.persistent_memory.load_context(user_id, 3)
        if context:
            logger.info(f"📚 加载持久化记忆: {user_id}")

    def _build_context(self, user_id: str, message: str, standard_json: Dict = None) -> str:
        """构建 LLM 上下文 - 完整版
    
        数据来源：
        1. soul_context - 当前会话状态（名字、情绪），来自 chat_agent
        2. persistent_memory - 长期记忆，来自文件存储
        3. profile - 用户偏好，来自会话内存
        4. history - 对话历史，来自会话内存
        5. 当前用户输入
        """
        history = self.conversations.get(user_id, [])
        profile = self.user_profiles.get(user_id, {})
        user_info = self.persistent_memory.get_user_info(user_id)
        parts = []

        # 1. 系统信息（soul_context，无标签，LLM 自然理解）
        if standard_json:
            params = standard_json.get("params", {})
            context = params.get("context", {})
            soul_context = context.get("soul", {})
            if soul_context and soul_context.get("user_known"):
                parts.append(soul_context.get("user_known"))

        # 2. 用户信息（profile + persistent_memory，去重）
        known_name = None
        for source in [profile, user_info]:
            if source.get("name") and not known_name:
                known_name = source.get("name")
                parts.append(f"用户姓名: {known_name}")

        # 3. 用户偏好（去重）
        prefs = []
        if profile.get("preferences"):
            prefs.extend(profile.get("preferences"))
        if user_info.get("preferences"):
            prefs.extend(user_info.get("preferences"))
        if prefs:
            parts.append(f"用户偏好: {', '.join(set(prefs))}")

        # 4. 会话历史
        for h in history[-6:]:
            parts.append(f"{h['role']}: {h['content']}")

        # 5. 当前用户输入
        parts.append(f"用户: {message}")

        return "\n".join(parts)

    def execute(self, message: Union[str, Dict], user_id: str = "guest") -> Dict:
        """
        执行对话 - 支持 2.5 层 JSON 规范
    
        Args:
            message: 字符串（兼容旧版）或 2.5 层标准 JSON
            user_id: 用户 ID（当 message 是字符串时使用）
        """
        # ============================================================
        # 1. 解析输入（支持 2.5 层 JSON 或纯字符串）
        # ============================================================
        raw_input = ""
        session_id = None
        thread_id = None
        turn = 0
        action = "chat"
        target = "text"
        keywords = []
        confidence = 0.85
        params = {}
    
        if isinstance(message, str):
            # 兼容旧版：纯字符串
            raw_input = message
            standard_json = None
        else:
            # 2.5 层 JSON
            standard_json = message
            raw_input = standard_json.get("raw_input", message.get("message", ""))
            session_id = standard_json.get("session_id")
            thread_id = standard_json.get("thread_id")
            turn = standard_json.get("turn", 0)
            action = standard_json.get("action", "chat")
            target = standard_json.get("target", "text")
            keywords = standard_json.get("keywords", [])
            confidence = standard_json.get("confidence", 0.85)
            params = standard_json.get("params", {})
            user_id = standard_json.get("user_id", user_id)
    
        if not raw_input:
            raw_input = message.get("raw_input", "") if isinstance(message, dict) else str(message)
    
        # ============================================================
        # 2. 从 2.5 层 JSON 中提取上下文
        # ============================================================
        context = params.get("context", {})
        memories = context.get("memories", [])
        emotion = context.get("emotion", {})
        soul = context.get("soul", {})
        soul_emotion = context.get("soul_emotion", {})
        history = context.get("history", [])
        suggestion = context.get("suggestion")
        has_dialect = context.get("has_dialect", False)
    
        # ============================================================
        # 3. 构建增强的 prompt
        # ============================================================
        enhanced_message = raw_input
    
        # 注入记忆
        if memories:
            memory_text = "\n".join([f"【记忆】用户之前说: {m.get('user', '')[:50]}" for m in memories[-3:]])
            enhanced_message = f"{enhanced_message}\n\n{memory_text}"
    
        # 注入情感（如果有）
        if emotion and emotion.get("dominant_emotion"):
            enhanced_message = f"[用户情绪: {emotion.get('dominant_emotion')}] {enhanced_message}"
    
        # 注入灵魂（如果有）
        if soul and soul.get("user_known"):
            enhanced_message = f"{soul.get('user_known')} {enhanced_message}"
    
        # 注入主动建议
        if suggestion:
            enhanced_message = f"{enhanced_message}\n\n[主动建议] {suggestion}"
    
        # ============================================================
        # 4. 调用原有处理逻辑
        # ============================================================
        logger.info(f"处理 {user_id}: {raw_input[:40]}...")
    
        # 加载持久化记忆
        self._load_persistent_memory(user_id)
    
        # 构建上下文
        context_str = self._build_context(user_id, enhanced_message)
    
        # 意图识别
        from core.lib.config_driven_router import config_router
        intent_result = config_router.route(raw_input)
        intent = intent_result.get('intent', 'chat')
        logger.info(f"意图识别: {intent}")
    
        # 检查缓存
        is_simple = len(raw_input) < 80 and "我叫" not in raw_input and "喜欢" not in raw_input
        if is_simple:
            cached = self._cache_get(raw_input)
            if cached:
                logger.info(f"⚡ 缓存命中: {raw_input[:30]}")
                return self._build_response(
                    standard_json=standard_json,
                    output_content=cached,
                    output_data={"cached": True, "agent": "cached"}
                )
    
        # 调用 LLM
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    self.llm_url,
                    json={
                        "model": "qwen2:1.5b-instruct",
                        "prompt": context_str,
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 256}
                    },
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
            
                if resp.status_code == 200:
                    result = resp.json()
                    response = result.get("response", "")
                
                    if response:
                        # 保存到会话历史
                        self.conversations[user_id].append({"role": "user", "content": raw_input})
                        self.conversations[user_id].append({"role": "assistant", "content": response})
                     
                        # 限制历史长度
                        if len(self.conversations[user_id]) > 20:
                            self.conversations[user_id] = self.conversations[user_id][-20:]
                    
                        # 持久化保存
                        self.persistent_memory.save_conversation(user_id, raw_input, response)
                    
                        # 缓存
                        if is_simple:
                            self._cache_set(raw_input, response)
                    
                        # 返回 2.5 层 JSON
                        return self._build_response(
                            standard_json=standard_json,
                            output_content=response,
                            output_data={
                                "agent": "chat_engine",
                                "intent": intent,
                                "memories_used": len(memories)
                            }
                        )
                    else:
                        if attempt < self.max_retries - 1:
                            continue
                        return self._build_response(
                            standard_json=standard_json,
                            output_content="抱歉，我暂时无法处理。",
                            status="failed",
                            output_data={"error": "empty_response"}
                        )
                else:
                    if attempt < self.max_retries - 1:
                        continue
                    return self._build_response(
                        standard_json=standard_json,
                        output_content=f"服务错误: {resp.status_code}",
                        status="failed",
                        output_data={"error": f"http_{resp.status_code}"}
                    )
            except requests.Timeout as e:
                logger.error(f"LLM 超时: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return self._build_response(
                    standard_json=standard_json,
                    output_content="服务响应超时，请稍后重试。",
                    status="failed",
                    output_data={"error": "timeout"}
                )
            except Exception as e:
                logger.error(f"异常: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return self._build_response(
                    standard_json=standard_json,
                    output_content=f"处理失败: {str(e)}",
                    status="failed",
                    output_data={"error": "exception"}
                )
    
        return self._build_response(
            standard_json=standard_json,
            output_content="服务不可用",
            status="failed",
            output_data={"error": "service_unavailable"}
        )


    def _build_response(self, standard_json: Dict, output_content: str, 
                        status: str = "completed", output_data: Dict = None) -> Dict:
        """构建 2.5 层 JSON 响应"""
        from datetime import datetime
    
        if output_data is None:
            output_data = {}
    
        if standard_json:
            # 基于 2.5 层 JSON 构建响应
            return {
                "version": "2.5",
                "session_id": standard_json.get("session_id"),
                "user_id": standard_json.get("user_id"),
                "thread_id": standard_json.get("thread_id"),
                "turn": standard_json.get("turn", 0) + 1,
                "raw_input": standard_json.get("raw_input", ""),
                "timestamp": datetime.now().isoformat(),
                "action": standard_json.get("action", "chat"),
                "target": standard_json.get("target", "text"),
                "keywords": standard_json.get("keywords", []),
                "confidence": standard_json.get("confidence", 0.85),
                "params": standard_json.get("params", {}),
                "output_type": "text",
                "output_content": output_content,
                "output_data": output_data,
                "status": status,
                "next": "done"
            }
        else:
            # 兼容旧版（没有标准 JSON 输入）
            return {
                "version": "2.5",
                "session_id": None,
                "user_id": "guest",
                "thread_id": None,
                "turn": 0,
                "raw_input": "",
                "timestamp": datetime.now().isoformat(),
                "action": "chat",
                "target": "text",
                "keywords": [],
                "confidence": 0.5,
                "params": {},
                "output_type": "text",
                "output_content": output_content,
                "output_data": output_data,
                "status": status,
                "next": "done"
            }


    def _add_reasoning_chain(self, question: str, answer: str) -> str:
        """添加推理链"""
        # 检测数学问题
        if any(op in question for op in ['+', '-', '*', '/', '计算', '等于']):
            return f"""【解题步骤】
1. 分析问题：{question}
2. 逐步计算
3. 得出结果

{answer}"""

        # 检测逻辑问题
        if any(word in question for word in ['如果', '那么', '因为', '所以', '推理']):
            return f"""【逻辑推理】
前提条件分析
    ↓
逻辑推导
    ↓
得出结论

{answer}"""

        return answer

chat_engine = UnifiedChatEngine()
