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
        # 动态获取项目根目录
        self.root = Path(__file__).parent.parent
        
        config_paths = [
            self.root / "config/config.yaml",
            Path("/etc/clawsjoy/config.yaml"),
        ]

        for path in config_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
                print(f"✅ 配置加载: {path}")
                # 确保 root 路径正确
                if 'paths' not in self._config:
                    self._config['paths'] = {}
                self._config['paths']['root'] = str(self.root)
                return

        # 默认配置
        self._config = {
            "version": "3.0",
            "services": {
                "gateway": {"port": 5002, "host": "0.0.0.0"},
                "file_service": {"port": 5003},
                "multi_agent": {"port": 5005},
                "doc_generator": {"port": 5008},
                "agent_api": {"port": 5010}
            },
            "paths": {"root": str(self.root)},
            "llm": {"endpoint": "http://127.0.0.1:11434", "default_model": "qwen2.5:7b"}
        }
        print("⚠️ 使用默认配置")

    def get(self, key, default=None):
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

config = Config()
