"""设置爬虫阈值"""

import sys

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")


class SetThresholdSkill:
    name = "set_threshold"
    description = "设置爬虫阈值参数"
    version = "1.0.0"
    category = "crawler"

    # 全局阈值配置
    _config = {
        "max_depth": 2,
        "max_pages": 20,
        "similarity_threshold": 0.85,
        "relevance_threshold": 0.6,
        "delay": 1,
    }

    def execute(self, params):
        import json
        from pathlib import Path

        # 更新配置
        for key in [
            "max_depth",
            "max_pages",
            "similarity_threshold",
            "relevance_threshold",
            "delay",
        ]:
            if key in params:
                self._config[key] = params[key]

        # 保存配置
        config_file = Path("data/crawler_config.json")
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(self._config, f, indent=2)

        # 同步到 SmartCrawler
        from src.skills.atomic.crawler.smart_crawler import SmartCrawlerSkill

        SmartCrawlerSkill.CONFIG.update(self._config)

        return {"success": True, "config": self._config, "message": "阈值配置已更新"}

    @classmethod
    def get_config(cls):
        return cls._config


skill = SetThresholdSkill()
