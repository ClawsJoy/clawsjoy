"""意图路由器单元测试"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from core.lib.smart_intent_router import smart_intent_router


class TestIntentRouter(unittest.TestCase):
    
    def test_math_intent(self):
        """测试数学意图识别"""
        result = smart_intent_router.route("100+200")
        self.assertEqual(result.get('intent'), 'math')
        
        result = smart_intent_router.route("计算 50 * 3")
        self.assertEqual(result.get('intent'), 'math')
    
    def test_code_intent(self):
        """测试代码意图识别"""
        result = smart_intent_router.route("写一个hello函数")
        self.assertEqual(result.get('intent'), 'code')
        
        result = smart_intent_router.route("def hello():")
        self.assertEqual(result.get('intent'), 'code')
    
    def test_translate_intent(self):
        """测试翻译意图识别"""
        result = smart_intent_router.route("翻译 hello")
        self.assertEqual(result.get('intent'), 'translate')
        
        result = smart_intent_router.route("hello的中文")
        self.assertEqual(result.get('intent'), 'translate')
    
    def test_chat_intent(self):
        """测试聊天意图识别"""
        result = smart_intent_router.route("你好")
        self.assertEqual(result.get('intent'), 'chat')


if __name__ == '__main__':
    unittest.main()
