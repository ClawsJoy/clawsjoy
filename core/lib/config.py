#!/usr/bin/env python3
"""Config - Config 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.lib.unified_config import unified_config


class Config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("config", {})
        return unified_config.get(f"config.{path}", default)


config = Config()
