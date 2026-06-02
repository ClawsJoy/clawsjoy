#!/usr/bin/env python3
"""Config Helper Mixin - Config Helper Mixin 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from core.lib.unified_config import unified_config


class ConfigHelperMixin:
    """配置读取辅助"""

    def get_agent_config(self, key: str, default=None):
        """读取 Agent 配置"""
        config_path = f"agents.{self.name}.{key}"
        return unified_config.get(config_path, default)

    def get_llm_config(self):
        """获取 LLM 配置"""
        return {
            "model": self.get_agent_config("llm.model", "qwen2.5:3b"),
            "temperature": self.get_agent_config("llm.temperature", 0.3),
            "timeout": self.get_agent_config("llm.timeout", 30),
        }
