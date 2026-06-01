"""增强语义理解引擎 - 使用本地向量"""

from typing import Any, Dict, List, Optional, Tuple,  Dict, List, Any, Optional
from datetime import datetime
from engine.lib.logger import engine_logger
from engine.embedding.local_embedding import local_embedding

class EnhancedSemanticEngine:
    """增强语义理解引擎"""
    
    def __init__(self):
        self.context_memory = {}
        self.embedding = local_embedding
        engine_logger.get().info("🧠 增强语义理解引擎已初始化 (本地向量)")
    
    def understand_with_context(self, text: str, user_id: str, 
                                  conversation_history: List[Dict] = None) -> Dict:
        """带上下文的语义理解"""
        # 1. 基础意图识别
        base_intent = self._base_intent(text)
        
        # 2. 向量相似度增强
        similar_intents = self._find_similar_intents(text)
        
        # 3. 上下文增强
        if conversation_history:
            context = self._extract_context(conversation_history)
            base_intent['context'] = context
        
        # 4. 用户画像增强
        user_context = self.context_memory.get(user_id, {})
        base_intent['user_context'] = user_context
        
        # 5. 置信度计算
        confidence = self._calculate_confidence(base_intent, conversation_history)
        base_intent['confidence'] = confidence
        base_intent['similar_intents'] = similar_intents
        
        # 6. 存储上下文
        self._update_context(user_id, text, base_intent)
        
        return base_intent
    
    def _base_intent(self, text: str) -> Dict:
        intents = {
            'greeting': ['你好', '您好', 'hi', 'hello'],
            'query': ['什么', '如何', '为什么', '哪个'],
            'action': ['帮我', '请', '需要', '想要'],
        }
        
        for intent, keywords in intents.items():
            if any(kw in text for kw in keywords):
                return {'intent': intent, 'entities': self._extract_entities(text)}
        
        return {'intent': 'unknown', 'entities': {}}
    
    def _find_similar_intents(self, text: str) -> List[Dict]:
        """基于向量查找相似意图"""
        # 预定义意图示例
        intent_examples = {
            'greeting': ['你好', '您好', '早上好', '下午好', '晚上好'],
            'query': ['这是什么', '如何做', '为什么', '什么时候'],
            'action': ['帮我做', '请回答', '需要帮助', '想要了解'],
            'code': ['写代码', '编程', '写函数', '写算法'],
            'weather': ['天气', '气温', '会不会下雨'],
        }
        
        results = []
        for intent, examples in intent_examples.items():
            best_sim = max(self.embedding.similarity(text, ex) for ex in examples)
            if best_sim > 0.3:
                results.append({'intent': intent, 'similarity': best_sim})
        
        return sorted(results, key=lambda x: -x['similarity'])[:3]
    
    def _extract_entities(self, text: str) -> Dict:
        import re
        entities = {}
        name_match = re.search(r'[我]叫([\u4e00-\u9fa5]{2,4})', text)
        if name_match:
            entities['name'] = name_match.group(1)
        num_match = re.search(r'\d+', text)
        if num_match:
            entities['number'] = num_match.group()
        return entities
    
    def _extract_context(self, history: List[Dict]) -> Dict:
        if not history:
            return {}
        recent = history[-5:]
        topics = [turn.get('intent', 'unknown') for turn in recent]
        return {'recent_intents': topics, 'conversation_length': len(history)}
    
    def _calculate_confidence(self, intent: Dict, history: List[Dict]) -> float:
        base = 0.7 if intent['intent'] != 'unknown' else 0.3
        if history and len(history) > 0:
            base = min(base + 0.1, 0.95)
        return base
    
    def _update_context(self, user_id: str, text: str, intent: Dict):
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {'history': [], 'preferences': {}}
        self.context_memory[user_id]['history'].append({
            'text': text, 'intent': intent, 'timestamp': datetime.now().isoformat()
        })
        if len(self.context_memory[user_id]['history']) > 50:
            self.context_memory[user_id]['history'] = self.context_memory[user_id]['history'][-50:]
    
    def get_stats(self) -> Dict:
        return {
            "users": len(self.context_memory),
            "total_history": sum(len(u['history']) for u in self.context_memory.values()),
            "embedding_ready": True
        }

enhanced_semantic = EnhancedSemanticEngine()
