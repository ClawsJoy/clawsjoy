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
        self.llm_url = "http://localhost:5012/chat"
        self.timeout = 120
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

    def _build_context(self, user_id: str, message: str) -> str:
        history = self.conversations.get(user_id, [])
        profile = self.user_profiles.get(user_id, {})
        
        parts = []
        
        # 从持久化记忆获取用户信息
        user_info = self.persistent_memory.get_user_info(user_id)
        if user_info.get('name'):
            parts.append(f"【用户】姓名: {user_info['name']}")
        if user_info.get('preferences'):
            parts.append(f"【用户】偏好: {', '.join(user_info['preferences'])}")
        
        if history:
            parts.append("【会话历史】")
            for h in history[-6:]:
                parts.append(f"{h['role']}: {h['content']}")
        
        parts.append(f"【当前】{message}")

        # 向量检索相关知识
        try:
            search_result = vector_knowledge_center.search(message, top_k=3)
            if search_result:
                parts.append("\n📚 相关知识：")
                for item in search_result[:3]:
                    if isinstance(item, dict):
                        content_text = item.get("content", item.get("text", ""))[:200]
                        if content_text:
                            parts.append(f"  • {content_text}")
        except Exception as e:
            logger.debug(f"向量检索失败: {e}")

        return "\n".join(parts)



    def execute(self, message, user_id: str = "guest") -> Dict:
        from core.lib.config_driven_router import config_router
        from core.lib.unified_intent_parser import unified_parser
        import uuid

        def generate_id() -> str:
            return uuid.uuid4().hex[:8]

        # 处理标准化 JSON 输入
        session_id = generate_id()
        thread_id = generate_id()
        turn = 0
    
        if isinstance(message, dict):
            # 提取会话信息
            session_id = message.get("session_id", generate_id())
            thread_id = message.get("thread_id", generate_id())
            turn = message.get("turn", 0)
            raw_input = message.get("raw_input", message.get("message", ""))
            action = message.get("action", "")
            target = message.get("target", "")
            keywords = message.get("keywords", [])
            confidence = message.get("confidence", 0.95)
        
            if raw_input:
                message = raw_input
            else:
                message = " ".join(keywords) if keywords else "chat"
        else:
            # 非标准化输入，使用意图解析器转换
            parse_result = unified_parser.parse(message)
            if parse_result.get("success"):
                parsed = parse_result.get("intent", {})
                action = parsed.get("action", "chat")
                target = parsed.get("target", "text")
                keywords = parsed.get("keywords", [])
                confidence = parsed.get("confidence", 0.8)
            else:
                action = "chat"
                target = "text"
                keywords = []
                confidence = 0.5
            raw_input = message

        # 确保 message 是字符串
        if not isinstance(message, str):
            message = str(message)

        logger.info(f"处理 {user_id}: {message[:40]}...")

        # 加载持久化记忆
        self._load_persistent_memory(user_id)

        # 使用现有意图路由器
        intent_result = config_router.route(message)
        intent = intent_result.get('intent', 'chat')
        logger.info(f"意图识别: {intent} (置信度: {intent_result.get('confidence', 0)})")

        # 根据意图调整处理策略
        is_simple = len(message) < 80 and "我叫" not in message and "喜欢" not in message
     
        # 检查缓存
        if is_simple:
            cached = self._cache_get(message)
            if cached:
                logger.info(f"⚡ 缓存命中: {message[:30]}")
                return self._build_standard_response(
                    raw_input=raw_input,
                    user_id=user_id,
                    session_id=session_id,
                    thread_id=thread_id,
                    turn=turn,
                    action=action,
                    target=target,
                    keywords=keywords,
                    confidence=confidence,
                    output_content=cached,
                    output_data={"cached": True, "agent": "cached"}
                )  

        context = self._build_context(user_id, message)

        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    self.llm_url,
                    json={"message": context},
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )

                if resp.status_code == 200:
                    result = resp.json()
                    response = result.get("response", "")

                    if response:
                        # 保存到会话历史
                        self.conversations[user_id].append({"role": "user", "content": message})
                        self.conversations[user_id].append({"role": "assistant", "content": response})

                        # 推理链增强
                        reasoning = None
                        if any(word in message for word in ['为什么', '怎么', '如何', '推理', '如果', '那么']):
                            reasoning = self._add_reasoning_chain(message, response)
                        final_response = reasoning if reasoning else response

                        # 限制历史长度
                        if len(self.conversations[user_id]) > 20:
                            self.conversations[user_id] = self.conversations[user_id][-20:]

                        # 持久化保存
                        self.persistent_memory.save_conversation(user_id, message, final_response)

                        # 缓存
                        if is_simple:
                            self._cache_set(message, final_response)
                    
                        # ✅ 返回标准化 JSON
                        return self._build_standard_response(
                            raw_input=raw_input,
                            user_id=user_id,
                            session_id=session_id,
                            thread_id=thread_id,
                            turn=turn,
                            action=action,
                            target=target,
                            keywords=keywords,
                            confidence=confidence,
                            output_content=final_response,
                            output_data={
                                "agent": "chat_engine",
                                "intent": intent,
                                "reasoning_applied": reasoning is not None
                            }
                        )
                    else:
                        if attempt < self.max_retries - 1:
                            continue
                        return self._build_standard_response(
                            raw_input=raw_input,
                            user_id=user_id,
                            session_id=session_id,
                            thread_id=thread_id,
                            turn=turn,
                            action=action,
                            target=target,
                            keywords=keywords,
                            confidence=0.3,
                            output_content="空响应",
                            status="failed",
                            output_data={"error": "empty_response"}
                        )
                else:
                    if attempt < self.max_retries - 1:
                        continue
                    return self._build_standard_response(
                        raw_input=raw_input,
                        user_id=user_id,
                        session_id=session_id,
                        thread_id=thread_id,
                        turn=turn,
                        action=action,
                        target=target,
                        keywords=keywords,
                        confidence=0.2,
                        output_content=f"HTTP {resp.status_code}",
                        status="failed",
                        output_data={"error": f"http_{resp.status_code}"}
                    )

            except requests.Timeout as e:
                logger.error(f"LLM 超时: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return self._build_standard_response(
                    raw_input=raw_input,
                    user_id=user_id,
                    session_id=session_id,
                    thread_id=thread_id,
                    turn=turn,
                    action=action,
                    target=target,
                    keywords=keywords,
                    confidence=0.1,
                    output_content="服务响应超时",
                    status="failed",
                    output_data={"error": "timeout"}
                )
            except requests.ConnectionError as e:
                logger.error(f"LLM 连接失败: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return self._build_standard_response(
                    raw_input=raw_input,
                    user_id=user_id,
                    session_id=session_id,
                    thread_id=thread_id,
                    turn=turn,
                    action=action,
                    target=target,
                    keywords=keywords,
                    confidence=0.1,
                    output_content="无法连接LLM服务",
                    status="failed",
                    output_data={"error": "connection_error"}
                )
            except Exception as e:
                logger.error(f"异常: {e}")
                if attempt < self.max_retries - 1:
                    continue
                return self._build_standard_response(
                    raw_input=raw_input,
                    user_id=user_id,
                    session_id=session_id,
                    thread_id=thread_id,
                    turn=turn,
                    action=action,
                    target=target,
                    keywords=keywords,
                    confidence=0.1,
                    output_content=str(e),
                    status="failed",
                    output_data={"error": "exception"}
                )

        return self._build_standard_response(
            raw_input=raw_input,
            user_id=user_id,
            session_id=session_id,
            thread_id=thread_id,
            turn=turn,
            action=action,
            target=target,
            keywords=keywords,
            confidence=0.1,
            output_content="服务不可用",
            status="failed",
            output_data={"error": "service_unavailable"}
        )


    def _build_standard_response(
        self,
        raw_input: str,
        user_id: str,
        session_id: str,
        thread_id: str,
        turn: int,
        action: str,
        target: str,
        keywords: list,
        confidence: float,
        output_content: str,
        output_data: dict = None,
        status: str = "completed",
        next_action: str = "done"
    ) -> Dict:
        """构建标准化 JSON v1.0 响应"""
        from datetime import datetime
    
        if output_data is None:
            output_data = {}
    
        return {
            "version": "1.0",
            "session_id": session_id,
            "user_id": user_id,
            "thread_id": thread_id,
            "turn": turn + 1,
            "raw_input": raw_input,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            "keywords": keywords,
            "confidence": confidence,
            "output_type": "text",
            "output_content": output_content,
            "output_data": output_data,
            "status": status,
            "next": next_action
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
