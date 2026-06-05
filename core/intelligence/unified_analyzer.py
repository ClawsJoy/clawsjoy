#!/usr/bin/env python3
"""Unified Analyzer - Unified Analyzer 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from core.lib.unified_config import unified_config

"""统一数据源分析器 - 配置驱动版"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.lib.data_source_manager import data_source_manager
from core.lib.unified_config import unified_config


class UnifiedAnalyzer:
    """统一分析器 - 配置驱动"""

    VERSION = "2.0.0"

    def __init__(self):
        host = unified_config.get("services.gateway.host", "127.0.0.1")
        port = unified_config.get("ports", {}).get("ollama", 11434)
        self.ollama_url = f"http://{host}:{port}"
        self._load_config()
        self.data_sources = {}

    def _load_config(self):
        """加载配置"""
        config_file = Path("config/driver/analyzer.yaml")
        if config_file.exists():
            with open(config_file, "r") as f:
                self.config = unified_config.get("analyzer", {})
        else:
            self.config = {
                "data_sources": [
                    {
                        "category": "workflow_outcome",
                        "description": "任务执行结果",
                        "enabled": True,
                        "weight": 0.3,
                    },
                    {
                        "category": "error_knowledge",
                        "description": "错误修复知识库",
                        "enabled": True,
                        "weight": 0.2,
                    },
                ],
                "llm": {
                    "model": unified_config.get_llm_config().get(
                        "default_model",
                        unified_config.get_llm_config().get(
                            "default_model", config_helper.get_llm_model()
                        ),
                    ),
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
                "analysis": {"max_samples_per_source": 5, "enable_llm_summary": True},
            }

    def collect_all_data(self) -> Dict:
        """收集所有数据源"""
        return data_source_manager.fetch_all()

    def analyze(self) -> Dict:
        """综合分析"""
        all_data = self.collect_all_data()

        result = {
            "timestamp": datetime.now().isoformat(),
            "sources": all_data.get("sources", {}),
            "summary": {},
            "insights": [],
            "suggestions": [],
        }

        # 计算健康度
        health_score = 85
        error_count = len(
            all_data.get("sources", {}).get("errors", {}).get("items", [])
        )
        if error_count > 0:
            health_score -= min(30, error_count)

        result["summary"]["health_score"] = max(0, health_score)
        result["summary"]["total_items"] = all_data.get("summary", {}).get(
            "total_items", 0
        )

        # 生成建议
        if error_count > 0:
            result["suggestions"].append(
                {
                    "level": "warning",
                    "message": f"发现 {error_count} 条错误，建议检查错误知识库",
                }
            )

        # 发送分析结果给决策者
        try:
            from core.lib.file_exchange import file_exchange

            file_exchange.send(
                to_agent="decision",
                data={
                    "from": "unified_analyzer",
                    "action": "analysis_report",
                    "type": "analysis_report",
                    "timestamp": result["timestamp"],
                    "health_score": result["summary"]["health_score"],
                    "suggestions": result.get("suggestions", []),
                    "summary": result["summary"],
                },
            )
            print(
                f"📤 分析结果已发送给决策者, 健康度: {result['summary']['health_score']}"
            )
        except Exception as e:
            print(f"⚠️ 发送分析结果失败: {e}")

        return result


unified_analyzer = UnifiedAnalyzer()
