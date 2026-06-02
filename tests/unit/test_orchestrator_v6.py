"""Orchestrator V6 单元测试"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestOrchestratorV6:
    """Orchestrator V6 测试"""

    def test_smart_route_code(self):
        """测试代码路由"""
        from core.agents.builtin.orchestrator_v6 import orchestrator_v6
        result = orchestrator_v6.smart_route("帮我写代码")
        assert result == "code_agent"

    def test_smart_route_weather(self):
        """测试天气路由"""
        from core.agents.builtin.orchestrator_v6 import orchestrator_v6
        result = orchestrator_v6.smart_route("今天天气")
        assert result == "weather_skill"

    def test_smart_route_translate(self):
        """测试翻译路由"""
        from core.agents.builtin.orchestrator_v6 import orchestrator_v6
        result = orchestrator_v6.smart_route("翻译这段话")
        assert result == "translate_agent"

    def test_intent_map_from_config(self):
        """测试 intent_map 从配置加载"""
        from core.agents.builtin.orchestrator_v6 import orchestrator_v6
        intent_map = orchestrator_v6._get_intent_map()
        assert len(intent_map) > 0
        assert "code" in intent_map or "code_agent" in intent_map
