#!/usr/bin/env python3
"""基础 Agent 类"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy_clean')


class BaseAgent:
    """所有 Agent 的基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.config = {}
    
    def log(self, message: str):
        """日志输出"""
        print(f"[{self.name}] {message}")
    
    def process(self, user_input: str, context=None):
        """处理请求（子类实现）"""
        raise NotImplementedError
    
    def get_status(self):
        """获取状态"""
        return {"name": self.name, "status": "running"}
