#!/usr/bin/env python3
"""Agent 自动发现 - 扫描 agents/ 目录"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Optional


class AgentDiscovery:
    """Agent 自动发现器"""

    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = Path(agents_dir)

    def discover_all(self) -> Dict[str, tuple]:
        """发现所有 Agent
        
        Returns:
            {"agent_name": ("module_path", "class_name")}
        """
        agents = {}

        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            if agent_dir.name.startswith("__"):
                continue

            agent_name = agent_dir.name

            # 检查是否有 V4 版本
            v4_file = agent_dir / "agent_v4.py"
            if v4_file.exists():
                class_name = self._extract_class_name(v4_file, "V4")
                if class_name:
                    module_path = f"agents.{agent_name}.agent_v4"
                    agents[agent_name] = (module_path, class_name)
                    continue

            # 检查是否有标准版本
            agent_file = agent_dir / "agent.py"
            if agent_file.exists():
                class_name = self._extract_class_name(agent_file)
                if class_name:
                    module_path = f"agents.{agent_name}.agent"
                    agents[agent_name] = (module_path, class_name)

        return agents

    def _extract_class_name(self, file_path: Path, suffix: str = "") -> Optional[str]:
        """从文件提取类名"""
        try:
            content = file_path.read_text()
            # 查找 class 定义
            import re
            pattern = rf'class\s+(\w+{suffix}?)\(.*BusinessAgent.*\):'
            matches = re.findall(pattern, content)
            if matches:
                return matches[0]
            # 备用：查找任何以 Agent 结尾的类
            pattern = r'class\s+(\w+Agent)\(.*\):'
            matches = re.findall(pattern, content)
            return matches[0] if matches else None
        except:
            return None

    def register_all(self, wisdom_factory):
        """注册所有发现的 Agent 到 wisdom_factory"""
        agents = self.discover_all()
        for name, (module_path, class_name) in agents.items():
            # 懒加载注册
            def make_loader(mod_path, cls_name):
                def loader():
                    try:
                        module = __import__(mod_path, fromlist=[cls_name])
                        return getattr(module, cls_name)
                    except Exception as e:
                        print(f"加载 {mod_path} 失败: {e}")
                        return None
                return loader

            if hasattr(wisdom_factory, '_register_lazy'):
                wisdom_factory._register_lazy(f"{name}_v4", make_loader(module_path, class_name))
            else:
                print(f"警告: wisdom_factory 没有 _register_lazy 方法")
        
        return agents


# 全局实例
agent_discovery = AgentDiscovery()
