#!/usr/bin/env python3
"""Api Discovery - Api Discovery 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


from pathlib import Path

import yaml

from core.lib.route_handlers import HANDLERS
from core.lib.route_registry import route_registry
from core.lib.unified_config import unified_config
from core.tenant.tenant_vector_index import tenant_index_manager


class APIDiscovery:
    """API 语义发现 - 让 API 可被自然语言发现"""

    def __init__(self):
        self._initialized = False

    def init_tenant_apis(self, tenant_id: str = "default"):
        """初始化租户 API 向量索引"""
        if self._initialized:
            return

        routes = route_registry.get_all_enabled()
        index = tenant_index_manager.get_index(tenant_id)

        indexed = 0
        for route in routes:
            path = route.get("path", "")
            method = route.get("method", "GET")
            handler = route.get("handler", "")
            description = route.get("description", "")

            # 构建 API 描述用于向量化
            api_description = f"{method} {path}: {description}"

            if path and handler:
                # 获取权限信息
                permissions = self._get_permissions(handler)

                index.index_route(
                    path,
                    method,
                    handler,
                    description=f"{description} 权限: {permissions.get('roles', [])}",
                )
                indexed += 1

        print(f"   🔍 已索引 {indexed} 个 API 端点")
        self._initialized = True
        return indexed

    def _get_permissions(self, handler_name: str) -> dict:
        """获取 handler 的权限配置"""
        # 从 Agent 配置中查找权限
        agent_config_file = Path("config/agents/registry") / f"{handler_name}.yaml"
        if agent_config_file.exists():
            with open(agent_config_file, "r") as f:
                config = yaml.safe_load(f)
                return config.get("permissions", {})
        return {}

    def discover(self, tenant_id: str, query: str, user_roles: list = None, n: int = 5):
        """语义发现 API"""
        index = tenant_index_manager.get_index(tenant_id)
        results = index.search_route(query, n)

        # 权限过滤
        if user_roles:
            filtered = []
            for r in results:
                # 检查用户是否有权限
                if self._check_permission(r.get("handler", ""), user_roles):
                    filtered.append(r)
            return filtered

        return results

    def _check_permission(self, handler_name: str, user_roles: list) -> bool:
        """检查用户是否有权限调用 API"""
        permissions = self._get_permissions(handler_name)
        required_roles = permissions.get("roles", [])

        if not required_roles:
            return True

        return any(role in user_roles for role in required_roles)

    def get_stats(self, tenant_id: str = "default"):
        """获取 API 索引统计"""
        index = tenant_index_manager.get_index(tenant_id)
        return index.get_stats()


api_discovery = APIDiscovery()
