"""引擎管理器 - 分层管理所有引擎"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class EngineManager:
    """引擎管理器 - 四层分类管理"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self._load_config()
        self._engines = {}
        self._load_engines()
        print(f"🔧 引擎管理器已初始化 (共 {len(self._engines)} 个引擎)")
    
    def _load_config(self):
        config_path = Path("config/engine_layers.yaml")
        if config_path.exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
    
    def _load_engines(self):
        """加载所有引擎"""
        engine_names = []
        for layer in ["expression_layer", "decision_layer", "orchestration_layer", "execution_layer"]:
            layer_config = self.config.get(layer, {})
            engines = layer_config.get("engines", [])
            engine_names.extend(engines)
        
        for name in engine_names:
            try:
                module = __import__(f"engine.{name}.core", fromlist=[f"{name}_engine"])
                if hasattr(module, f"{name}_engine"):
                    self._engines[name] = getattr(module, f"{name}_engine")
                    print(f"  ✅ 加载引擎: {name}")
                else:
                    print(f"  ⚠️ 引擎 {name} 未找到实例")
            except Exception as e:
                print(f"  ❌ 引擎 {name} 加载失败: {e}")
    
    def get_engine(self, name: str):
        """获取引擎"""
        return self._engines.get(name)
    
    def get_layer_engines(self, layer: str) -> List:
        """获取某层的所有引擎"""
        layer_config = self.config.get(layer, {})
        engines = []
        for name in layer_config.get("engines", []):
            if name in self._engines:
                engines.append(self._engines[name])
        return engines
    
    def get_all_engines(self) -> Dict:
        return self._engines


engine_manager = EngineManager()
