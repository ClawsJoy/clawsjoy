#!/usr/bin/env python3
"""Loader - Loader 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigLoader:
    """配置加载器"""

    def __init__(self):
        self.config_dir = Path("config/v5")

    @lru_cache(maxsize=128)
    def load(self, name: str) -> Dict[str, Any]:
        """加载配置"""
        config_file = self.config_dir / f"{name}.yaml"
        if not config_file.exists():
            return {}
        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}

    def reload(self):
        """热重载"""
        self.load.cache_clear()


config = ConfigLoader()
