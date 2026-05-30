#!/usr/bin/env python3
"""Agent Marketplace - Agent Marketplace 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
"""Agent 市场 - 下载、安装、管理专业 Agent"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class AgentMarketplace:
    """Agent 商品市场"""
    
    def __init__(self):
        self.products_file = Path("config/agent_products.yaml")
        self.installed_dir = Path(f"{get_data_root()}/installed_agents")
        self.installed_dir.mkdir(parents=True, exist_ok=True)
        self._load_products()
        self._load_installed()
    
    def _load_products(self):
        import yaml
        if self.products_file.exists():
            with open(self.products_file, 'r') as f:
                data = unified_config.get("marketplace")
                self.products = data.get('products', {})
                self.bundles = data.get('bundles', {})
        else:
            self.products = {}
            self.bundles = {}
    
    def _load_installed(self):
        installed_file = self.installed_dir / "installed.json"
        if installed_file.exists():
            with open(installed_file, 'r') as f:
                self.installed = json.load(f)
        else:
            self.installed = {"agents": [], "bundles": []}
    
    def _save_installed(self):
        installed_file = self.installed_dir / "installed.json"
        with open(installed_file, 'w') as f:
            json.dump(self.installed, f, indent=2)
    
    def list_products(self, category: str = None) -> List[Dict]:
        """列出可购买的商品"""
        products = list(self.products.values())
        if category:
            products = [p for p in products if p.get('category') == category]
        return products
    
    def get_product(self, product_id: str) -> Dict:
        return self.products.get(product_id, {})
    
    def install(self, user_id: str, product_id: str) -> Dict:
        """安装 Agent 商品"""
        product = self.get_product(product_id)
        if not product:
            return {"success": False, "error": "商品不存在"}

        # 检查是否已安装
        for installed in self.installed["agents"]:
            if installed["product_id"] == product_id and installed["user_id"] == user_id:
                return {"success": False, "error": "已安装"}

        # 安装记录
        install_record = {
            "product_id": product_id,
            "name": product.get('name'),
            "user_id": user_id,
            "installed_at": datetime.now().isoformat(),
            "version": product.get('version'),
            "capabilities": product.get('capabilities', [])
        }

        self.installed["agents"].append(install_record)
        self._save_installed()

        # 创建用户专属配置
        user_config_dir = Path(funified_config.get("paths.users_dir", f"{get_data_root()}/users/") + "/{user_id}/agents/{product_id}")
        user_config_dir.mkdir(parents=True, exist_ok=True)

        # 复制技能文件（如果需要）
        for skill in product.get('skills_included', []):
            source = Path(f"skills/development/{skill}.py")
            if source.exists():
                target = user_config_dir / f"{skill}.py"
                shutil.copy(source, target)

        return {
            "success": True,
            "message": f"✅ 已安装 {product.get('name')}",
            "install_path": str(user_config_dir)
        }
    
    def uninstall(self, user_id: str, product_id: str) -> Dict:
        """卸载 Agent"""
        self.installed["agents"] = [
            a for a in self.installed["agents"]
            if not (a["product_id"] == product_id and a["user_id"] == user_id)
        ]
        self._save_installed()

        return {"success": True, "message": f"已卸载 {product_id}"}
    
    def get_installed(self, user_id: str) -> List[Dict]:
        """获取用户已安装的 Agent"""
        return [a for a in self.installed["agents"] if a["user_id"] == user_id]
    
    def get_demo_code(self, product_id: str) -> str:
        """获取演示代码"""
        demos = {
            "frontend_master": '''
<!DOCTYPE html>
<html>
<head><title>前端大师演示</title>
<style>
body { background: #0a0a1a; color: #00f3ff; font-family: monospace; }
.container { max-width: 800px; margin: 100px auto; text-align: center; }
.glow-btn { padding: 12px 30px; background: transparent; border: 2px solid #00f3ff; color: #00f3ff; cursor: pointer; transition: 0.3s; }
.glow-btn:hover { box-shadow: 0 0 20px #00f3ff; }
</style>
</head>
<body>
<div class="container">
<h1>✨ 前端开发大师</h1>
<p>已安装成功！开始使用 AI 辅助开发</p>
<button class="glow-btn" onclick="alert('AI 助手已就绪')">开始使用</button>
</div>
</body>
</html>
'''
        }
        return demos.get(product_id, "<h1>演示页面</h1>")

agent_marketplace = AgentMarketplace()
