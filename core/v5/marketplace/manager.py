#!/usr/bin/env python3
"""Manager - Manager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import importlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class MarketplaceManager:
    """Agent 市场管理器"""

    def __init__(self):
        self.plugins_dir = Path(f"{config_helper.get_data_root()}/v5/plugins")
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.installed: Dict[str, Dict] = {}
        self._load_installed()

    def _load_installed(self):
        """加载已安装插件"""
        manifest_file = self.plugins_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                self.installed = json.load(f)

    def _save_installed(self):
        """保存安装记录"""
        with open(self.plugins_dir / "manifest.json", "w") as f:
            json.dump(self.installed, f, indent=2)

    def list_available(self) -> List[Dict]:
        """列出可用插件"""
        return [
            {
                "id": "web_search",
                "name": "网页搜索",
                "version": "1.0.0",
                "description": "搜索互联网信息",
                "author": "ClawsJoy",
                "price": "free",
            },
            {
                "id": "news_reader",
                "name": "新闻阅读",
                "version": "1.0.0",
                "description": "获取最新新闻",
                "author": "ClawsJoy",
                "price": "free",
            },
            {
                "id": "weather",
                "name": "天气查询",
                "version": "1.0.0",
                "description": "查询实时天气",
                "author": "ClawsJoy",
                "price": "free",
            },
            {
                "id": "calculator",
                "name": "高级计算器",
                "version": "1.0.0",
                "description": "数学计算和表达式求值",
                "author": "ClawsJoy",
                "price": "free",
            },
        ]

    def install(self, plugin_id: str) -> Dict:
        """安装插件"""
        if plugin_id in self.installed:
            return {"success": False, "error": "Already installed"}

        # 创建插件目录
        plugin_dir = self.plugins_dir / plugin_id
        plugin_dir.mkdir(exist_ok=True)

        # 创建插件配置
        plugin_config = {
            "id": plugin_id,
            "installed_at": datetime.now().isoformat(),
            "enabled": True,
            "config": {},
        }

        self.installed[plugin_id] = plugin_config
        self._save_installed()

        return {"success": True, "message": f"Plugin {plugin_id} installed"}

    def uninstall(self, plugin_id: str) -> Dict:
        """卸载插件"""
        if plugin_id not in self.installed:
            return {"success": False, "error": "Not installed"}

        del self.installed[plugin_id]
        self._save_installed()

        return {"success": True, "message": f"Plugin {plugin_id} uninstalled"}

    def get_installed(self) -> List[Dict]:
        """获取已安装插件"""
        return [{"id": pid, **info} for pid, info in self.installed.items()]


marketplace = MarketplaceManager()
