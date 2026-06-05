#!/usr/bin/env python3
"""Set Config - Set Config 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""配置管理技能 - 设置阈值和清理参数"""
import json
from pathlib import Path


class SetConfigSkill:
    name = "set_config"
    description = "设置采集阈值和清理参数"
    version = "1.0.0"
    category = "maintenance"

    def execute(self, params):
        config_file = Path("data/topic_config.json")
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
        else:
            config = {}

        # 更新配置
        for key in ["threshold", "top_k", "retention_days", "cron"]:
            if key in params:
                config[key] = params[key]

        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        return {"success": True, "config": config, "message": f"配置已更新"}


skill = SetConfigSkill()
