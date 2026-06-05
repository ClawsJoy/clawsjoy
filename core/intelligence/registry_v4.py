#!/usr/bin/env python3
"""Registry V4 - Registry V4 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import importlib.util
from pathlib import Path
from typing import Any, Dict


class IntelligenceRegistry:
    VERSION = "4.0.0"

    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self._discover_modules()

    def _discover_modules(self):
        """发现并注册所有智能模块"""
        intelligence_dir = Path(__file__).parent

        # 使用修复后的模块
        modules = {
            "predictor": "predictor.py",
            "decision_engine": "decision_engine.py",
            "learner": "learner.py",
            "closed_loop": "closed_loop.py",
            "analyzer": "analyzer.py",
            "success_monitor": "success_monitor_v1.0.01_20260517.py",
        }

        for name, filename in modules.items():
            file_path = intelligence_dir / filename
            if file_path.exists():
                try:
                    spec = importlib.util.spec_from_file_location(name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # 获取主要对象
                    if hasattr(module, name):
                        self.modules[name] = getattr(module, name)
                    elif hasattr(module, "predictor") and name == "predictor":
                        self.modules[name] = module.predictor
                    elif (
                        hasattr(module, "decision_engine") and name == "decision_engine"
                    ):
                        self.modules[name] = module.decision_engine
                    elif hasattr(module, "learner") and name == "learner":
                        self.modules[name] = module.learner
                    elif hasattr(module, "closed_loop") and name == "closed_loop":
                        self.modules[name] = module.closed_loop
                    elif hasattr(module, "analyzer") and name == "analyzer":
                        self.modules[name] = module.analyzer
                    else:
                        self.modules[name] = module
                    print(f"✅ 已注册: {name}")
                except Exception as e:
                    print(f"⚠️ 注册失败 {name}: {e}")
            else:
                print(f"⚠️ 文件不存在: {filename}")

    def get(self, name: str):
        return self.modules.get(name)

    def list_modules(self) -> list:
        return list(self.modules.keys())

    def get_status(self) -> dict:
        return {
            "version": self.VERSION,
            "modules": self.list_modules(),
            "total": len(self.modules),
        }


registry = IntelligenceRegistry()

if __name__ == "__main__":
    print(f"\n智能注册中心 v{registry.VERSION}")
    print(f"已注册: {registry.list_modules()}")
