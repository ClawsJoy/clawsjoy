"""keywords.yaml 配置测试"""

import pytest
import yaml
from pathlib import Path


class TestKeywordsConfig:
    """统一配置测试"""

    @pytest.fixture
    def config(self):
        with open("config/keywords.yaml", "r") as f:
            return yaml.safe_load(f)

    def test_agent_capabilities_exists(self, config):
        """测试 agent_capabilities 存在"""
        assert "agent_capabilities" in config
        assert len(config["agent_capabilities"]) > 0

    def test_code_agent_exists(self, config):
        """测试 code_agent 存在"""
        caps = config.get("agent_capabilities", {})
        assert "code_agent" in caps
        assert "写代码" in caps["code_agent"]["capable_of"]

    def test_weather_skill_exists(self, config):
        """测试 weather_skill 存在"""
        caps = config.get("agent_capabilities", {})
        assert "weather_skill" in caps
        assert "天气" in caps["weather_skill"]["capable_of"]

    def test_priority_range(self, config):
        """测试优先级在 1-100 范围内"""
        caps = config.get("agent_capabilities", {})
        for name, cap in caps.items():
            priority = cap.get("priority", 10)
            assert 1 <= priority <= 100, f"{name} priority {priority} out of range"
