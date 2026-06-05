#!/usr/bin/env python3
"""Agent Packager - Agent Packager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from core.lib.config_helper import (
    get_data_root,
    get_embedding_model,
    get_gateway_port,
    get_llm_endpoint,
    get_llm_model,
    get_timeout,
)
from core.lib.unified_config import unified_config

"""Agent 打包服务 - 用户自定义 Agent 上载、打包、发布"""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class AgentPackager:
    """Agent 打包器 - 支持用户自定义 Agent 上载"""

    def __init__(self):
        self.upload_dir = Path(f"{get_data_root()}/user_agents")
        self.package_dir = Path(f"{get_data_root()}/agent_packages")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.package_dir.mkdir(parents=True, exist_ok=True)
        self._load_registry()

    def _load_registry(self):
        registry_file = self.upload_dir / "registry.json"
        if registry_file.exists():
            with open(registry_file, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {"pending": [], "approved": [], "rejected": []}

    def _save_registry(self):
        registry_file = self.upload_dir / "registry.json"
        with open(registry_file, "w") as f:
            json.dump(self.registry, f, indent=2)

    def create_agent_template(self, user_id: str, agent_config: Dict) -> Dict:
        """创建 Agent 模板"""
        agent_id = f"custom_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        agent_dir = self.upload_dir / user_id / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        # 生成 Agent 配置文件
        config = {
            "id": agent_id,
            "name": agent_config.get("name", "自定义Agent"),
            "version": "1.0.0",
            "author": user_id,
            "description": agent_config.get("description", ""),
            "category": agent_config.get("category", "custom"),
            "price": agent_config.get("price", 0),
            "capabilities": agent_config.get("capabilities", []),
            "prompt": agent_config.get("prompt", ""),
            "created_at": datetime.now().isoformat(),
        }

        with open(agent_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        # 生成 Agent 技能代码
        skill_code = self._generate_skill_code(config)
        with open(agent_dir / "skill.py", "w") as f:
            f.write(skill_code)

        # 提交审核
        self.registry["pending"].append(
            {
                "agent_id": agent_id,
                "user_id": user_id,
                "name": agent_config.get("name"),
                "submitted_at": datetime.now().isoformat(),
            }
        )
        self._save_registry()

        return {
            "success": True,
            "agent_id": agent_id,
            "message": f"Agent [{agent_config.get('name')}] 已提交审核",
        }

    def _generate_skill_code(self, config: Dict) -> str:
        """生成 Agent 技能代码"""
        prompt = config.get("prompt", "你是智能助手，帮助用户解决问题。")

        return f'''"""
{config.get('name')} - 自定义 Agent
作者: {config.get('author')}
创建时间: {config.get('created_at')}
"""

from core.lib.smart_adapter import smart_adapter

class CustomAgent:
    """自定义 Agent - {config.get('description', '')}"""
    
    def __init__(self):
        self.name = "{config.get('name')}"
        self.prompt = \"\"\"{prompt}\"\"\"
    
    def execute(self, params: dict) -> dict:
        action = params.get('action', 'chat')
        message = params.get('message', '')

        if action == 'chat':
            full_prompt = f"{{self.prompt}}\\n\\n用户: {{message}}\\n助手:"
            response = smart_adapter.generate(full_prompt, auto_select=True)
            return {{"success": True, "response": response}}

        return {{"success": False, "error": "未知操作"}}

skill = CustomAgent()
'''

    def approve_agent(self, agent_id: str) -> Dict:
        """审核通过 Agent"""
        for item in self.registry["pending"]:
            if item["agent_id"] == agent_id:
                self.registry["pending"].remove(item)
                self.registry["approved"].append(item)

                # 打包
                package_path = self._package_agent(agent_id)

                # 添加到商品列表
                self._add_to_marketplace(agent_id)

                self._save_registry()
                return {
                    "success": True,
                    "package_path": package_path,
                    "message": f"Agent [{item['name']}] 已通过审核并打包",
                }

        return {"success": False, "error": "Agent 不存在"}

    def _package_agent(self, agent_id: str) -> str:
        """打包 Agent"""
        # 找到 agent 目录
        for user_dir in self.upload_dir.iterdir():
            if user_dir.is_dir():
                agent_dir = user_dir / agent_id
                if agent_dir.exists():
                    package_file = self.package_dir / f"{agent_id}.zip"
                    with zipfile.ZipFile(package_file, "w") as zf:
                        for f in agent_dir.glob("*"):
                            zf.write(f, f.name)
                    return str(package_file)
        return ""

    def _add_to_marketplace(self, agent_id: str):
        """添加到商品列表"""
        # 读取配置
        for user_dir in self.upload_dir.iterdir():
            if user_dir.is_dir():
                config_file = user_dir / agent_id / "config.json"
                if config_file.exists():
                    with open(config_file, "r") as f:
                        config = json.load(f)

                    # 更新 market 配置
                    market_file = Path("config/agent_products.yaml")
                    if market_file.exists():
                        import yaml

                        with open(market_file, "r") as f:
                            market = unified_config.get("packager")

                        if "products" not in market:
                            market["products"] = {}

                        market["products"][agent_id] = {
                            "id": agent_id,
                            "name": config.get("name"),
                            "version": config.get("version"),
                            "price": config.get("price"),
                            "category": config.get("category"),
                            "description": config.get("description"),
                            "capabilities": config.get("capabilities", []),
                        }

                        with open(market_file, "w") as f:
                            yaml.dump(market, f, allow_unicode=True)
                    break

    def get_pending(self) -> List[Dict]:
        """获取待审核列表"""
        return self.registry["pending"]


agent_packager = AgentPackager()
