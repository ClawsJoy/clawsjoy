"""统一配置管理"""
import os
import yaml
from pathlib import Path

class Config:
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """加载配置文件"""
        config_paths = [
            Path("config/config.yaml"),
            Path("/mnt/d/clawsjoy/config/config.yaml"),
        ]
        
        for path in config_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
                print(f"✅ 配置加载: {path}")
                return
        
        # 默认配置
        self._config = self._default_config()
        print("⚠️ 使用默认配置")
    
    def _default_config(self):
        return {
            "services": {"gateway": {"port": 5002}},
            "llm": {"endpoint": "http://127.0.0.1:11434", "default_model": "qwen2.5:7b"},
            "paths": {"root": "/mnt/d/clawsjoy"}
        }
    
    def get(self, key, default=None):
        """获取配置值，支持点号分隔，如 'services.gateway.port'"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    @property
    def all(self):
        return self._config

# 全局配置实例
config = Config()
