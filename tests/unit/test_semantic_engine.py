"""语义理解引擎单元测试"""

import pytest
from engine.semantic.core import semantic_engine

class TestSemanticEngine:
    """语义理解引擎测试"""
    
    def test_understand_greeting(self):
        """测试问候意图"""
        result = semantic_engine.understand("你好")
        assert result.intent == "greeting"
        assert result.confidence > 0.5
    
    def test_understand_name_set(self):
        """测试名字设置意图"""
        result = semantic_engine.understand("我叫张三")
        assert result.intent == "name_set"
        assert 'name' in result.entities
    
    def test_understand_weather(self):
        """测试天气意图"""
        result = semantic_engine.understand("北京天气")
        assert result.intent == "weather"
    
    def test_understand_code(self):
        """测试代码意图"""
        result = semantic_engine.understand("写一个排序函数")
        assert result.intent == "code"
    
    def test_understand_translate(self):
        """测试翻译意图"""
        result = semantic_engine.understand("把hello翻译成中文")
        assert result.intent == "translate"
    
    def test_understand_calculate(self):
        """测试计算意图"""
        result = semantic_engine.understand("1+2等于多少")
        assert result.intent == "calculate"
    
    def test_get_stats(self):
        """测试统计信息"""
        stats = semantic_engine.get_stats()
        assert 'intents' in stats or 'status' in stats
