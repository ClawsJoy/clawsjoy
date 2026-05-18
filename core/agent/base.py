#!/usr/bin/env python3
"""基础 Agent 类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """所有 Agent 的基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.context = {}
    
    @abstractmethod
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户输入，返回结果"""
        pass
    
    def update_context(self, key: str, value: Any):
        """更新上下文"""
        self.context[key] = value
    
    def get_context(self, key: str, default=None) -> Any:
        """获取上下文"""
        return self.context.get(key, default)
    
    def log(self, message: str):
        """记录日志"""
        logger.info(f"[{self.name}] {message}")
