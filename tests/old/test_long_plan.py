import unittest
from core.lib.chat_engine import UnifiedChatEngine

class TestLongPlan(unittest.TestCase):
    def setUp(self):
        self.engine = UnifiedChatEngine()
    
    def test_is_long_plan_video(self):
        self.assertTrue(self.engine._is_long_plan("帮我制作AI短视频"))
    
    def test_is_long_plan_short(self):
        self.assertFalse(self.engine._is_long_plan("你好"))
    
    def test_is_long_plan_with_keywords(self):
        self.assertTrue(self.engine._is_long_plan("先写脚本，然后生成配图，最后翻译"))

if __name__ == "__main__":
    unittest.main()
