#!/usr/bin/env python3
"""统一配置加载器 v1.0.00 - 所有配置的单一入口"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache


class ConfigLoader:
    """统一配置加载器 - 替代所有硬编码"""
    
    VERSION = "1.0.00"
    
    def __init__(self):
        self.root = Path("/mnt/d/clawsjoy_clean")
        self.config_dir = self.root / "config" / "driver"
        self._configs = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有配置"""
        config_files = [
            "thresholds.yaml", "optimization.yaml", "tasks.yaml",
            "ports.yaml", "paths.yaml", "monitoring.yaml", "resources.yaml"
        ]
        
        for filename in config_files:
            file_path = self.config_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    if filename.endswith('.yaml'):
                        self._configs[filename.replace('.yaml', '')] = yaml.safe_load(f)
                    elif filename.endswith('.json'):
                        self._configs[filename.replace('.json', '')] = json.load(f)
            else:
                self._configs[filename.replace('.yaml', '')] = {}
    
    @lru_cache(maxsize=256)
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔"""
        parts = key.split('.')
        value = self._configs
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def get_port(self, service: str) -> int:
        """获取服务端口"""
        return self.get(f'ports.services.{service}', 5000)
    
    def get_path(self, name: str) -> Path:
        """获取路径"""
        path_str = self.get(f'paths.paths.{name}', f'./{name}')
        if path_str.startswith('./'):
            return self.root / path_str[2:]
        return Path(path_str)
    
    def get_threshold(self, name: str) -> float:
        """获取阈值"""
        return self.get(f'thresholds.{name}', 0.5)
    
    def is_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        return self.get(f'optimization.{feature}', False)
    
    def reload(self):
        """重新加载配置"""
        self._configs.clear()
        self._load_all()
        self.get.cache_clear()
        print("✅ 配置已重新加载")
    
    def get_status(self) -> Dict:
        """获取配置状态"""
        return {
            "version": self.VERSION,
            "config_dir": str(self.config_dir),
            "loaded_files": list(self._configs.keys()),
            "cache_size": self.get.cache_info().currsize
        }


# 全局实例
config = ConfigLoader()


if __name__ == "__main__":
    print(f"统一配置加载器 v{config.VERSION}")
    print(f"状态: {config.get_status()}")
    print(f"\n端口: gateway={config.get_port('gateway')}")
    print(f"路径: data={config.get_path('data')}")
    print(f"阈值: quality_min_score={config.get_threshold('quality_min_score')}")
    print(f"优化开关: enable_quality_scoring={config.is_enabled('enable_quality_scoring')}")
