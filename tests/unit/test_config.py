#!/usr/bin/env python3
"""配置模块单元测试"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestConfig(unittest.TestCase):
    
    def test_config_loader(self):
        from lib.config_loader import config
        self.assertIsNotNone(config)
        self.assertEqual(config.VERSION, "1.0.00")
    
    def test_config_get(self):
        from lib.config_loader import config
        port = config.get_port('gateway')
        self.assertEqual(port, 5002)
    
    def test_driver_config(self):
        from lib.driver_loader import driver_loader
        manifest = driver_loader.get_driver_manifest()
        self.assertIn('version', manifest)


class TestSecurity(unittest.TestCase):
    
    def test_secret_hook(self):
        from lib.secret_hook import secret_hook
        self.assertIsNotNone(secret_hook)
    
    def test_desensitization(self):
        from lib.security_hook import security_hook
        safe, _, _ = security_hook.check_input("正常内容")
        self.assertTrue(safe)


class TestAgent(unittest.TestCase):
    
    def test_agent_registry(self):
        from lib.agent_registry import agent_registry
        stats = agent_registry.get_stats()
        self.assertIn('total', stats)


if __name__ == '__main__':
    unittest.main()
