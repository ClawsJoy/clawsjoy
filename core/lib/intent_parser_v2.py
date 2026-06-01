"""意图解析器 V2 - 配置驱动，支持热重载"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class IntentParserV2:
    """配置驱动的意图解析器"""
    
    _instance = None
    _config = None
    _config_file = Path("config/intents.yaml")
    _last_modified = 0
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        if self._config_file.exists():
            with open(self._config_file, 'r') as f:
                self._config = yaml.safe_load(f)
                self._last_modified = self._config_file.stat().st_mtime
        else:
            self._config = {"intents": {}}
    
    def _check_reload(self):
        """检查是否需要热重载"""
        if self._config_file.exists():
            mtime = self._config_file.stat().st_mtime
            if mtime > self._last_modified:
                self._load_config()
                print("🔄 意图配置已热重载")
    
    def parse(self, user_input: str) -> Dict:
        """解析用户输入"""
        self._check_reload()
        
        user_input_lower = user_input.lower()
        intents = self._config.get('intents', {})
        
        # 按优先级排序（高优先级先匹配）
        sorted_intents = sorted(
            intents.items(),
            key=lambda x: x[1].get('priority', 0),
            reverse=True
        )
        
        for intent_key, intent_config in sorted_intents:
            keywords = intent_config.get('keywords', [])
            for keyword in keywords:
                # 支持正则表达式匹配
                if keyword.startswith('.*') or keyword.endswith('.*'):
                    if re.search(keyword, user_input_lower):
                        return self._build_result(intent_key, intent_config, user_input)
                else:
                    if keyword in user_input_lower:
                        return self._build_result(intent_key, intent_config, user_input)
        
        # 默认返回
        return {
            "intent": "general",
            "skills": ["chat_agent"],
            "confidence": 0.3,
            "message": "未识别明确意图"
        }
    
    def _build_result(self, intent_key: str, intent_config: Dict, user_input: str) -> Dict:
        """构建返回结果"""
        result = {
            "intent": intent_key,
            "name": intent_config.get('name', intent_key),
            "skills": intent_config.get('skills', ['chat_agent']),
            "confidence": 0.85,
            "message": f"识别到{intent_config.get('name', intent_key)}意图"
        }
        
        # 实体提取
        extractors = intent_config.get('extractors', [])
        for extractor in extractors:
            entities = self._extract_entities(user_input, extractor)
            if entities:
                result['entities'] = entities
        
        return result
    
    def _extract_entities(self, text: str, extractor_name: str) -> Dict:
        """提取实体"""
        extractors_config = self._config.get('extractors', {})
        extractor_config = extractors_config.get(extractor_name, {})
        
        if extractor_name == 'name':
            patterns = extractor_config.get('patterns', [])
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return {"name": match.group(1)}
        
        elif extractor_name == 'city':
            cities = extractor_config.get('list', [])
            for city in cities:
                if city in text:
                    return {"city": city}
        
        return {}
    
    def get_intent(self, user_input: str) -> str:
        """快速获取意图名称"""
        return self.parse(user_input).get('intent', 'unknown')
    
    def reload(self):
        """手动重载配置"""
        self._load_config()
        return {"success": True, "message": "意图配置已重载"}

intent_parser_v2 = IntentParserV2()

# 兼容原有接口
intent_parser = intent_parser_v2
