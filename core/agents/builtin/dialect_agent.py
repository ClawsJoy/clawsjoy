#!/usr/bin/env python3
"""Dialect Agent - Dialect Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent


class DialectAgent(SmartAgent):
    """方言处理 Agent"""

    name = "dialect_agent"
    description = "方言识别和转换"
    version = "1.0.0"


    def __init__(self, user_id: str = "default"):
        self._load_agent_config()
        super().__init__(user_id=user_id)
        self._load_config()
        self._load_dialects()
        print("🗣️ 方言Agent 初始化完成")

    def _load_config(self):
        """加载配置"""
        import yaml
        from pathlib import Path
        
        config_file = Path(f"agents/{self.name}/dialects.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.dialect_config = yaml.safe_load(f)
        else:
            self.dialect_config = {"supported_dialects": []}
    
    def _load_dialects(self):
        """从配置加载方言列表"""
        self.dialects = [
            d.get('name') for d in self.dialect_config.get('supported_dialects', [])
            if d.get('enabled', True)
        ]

    def detect(self, text: str) -> Dict:
        """检测方言"""
        return {"text": text[:50], "detected": "普通话", "confidence": 0.9}

    def convert(self, text: str, target: str = "普通话") -> Dict:
        """转换方言"""
        return {"original": text[:50], "target": target, "converted": text[:50]}

    def get_stats(self) -> Dict:
        return {"name": self.name, "version": self.version, "supported_dialects": len(self.dialects)}


# dialect_agent = DialectAgent()  # 注释：改为按需创建


    def process(self, message: str, **kwargs) -> dict:
        """处理方言相关请求"""
        msg = message.lower()
        
        # 方言识别
        dialects = {
            "粤语": ["粤语", "广东话", "cantonese"],
            "四川话": ["四川话", "川话"],
            "东北话": ["东北话", "东北方言"],
            "上海话": ["上海话", "沪语"],
            "闽南语": ["闽南语", "台语"],
        }
        
        detected = None
        for name, keywords in dialects.items():
            if any(kw in msg for kw in keywords):
                detected = name
                break
        
        if detected:
            return {
                "success": True,
                "response": f"检测到方言: {detected}",
                "dialect": detected,
                "agent": self.name
            }
        else:
            return {
                "success": True,
                "response": "我可以帮你识别和转换方言，支持粤语、四川话、东北话、上海话、闽南语",
                "capabilities": list(dialects.keys()),
                "agent": self.name
            }
