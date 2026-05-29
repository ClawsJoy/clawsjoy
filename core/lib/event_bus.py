from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""事件总线 - 事件驱动架构"""
from typing import Dict, List, Callable
from collections import defaultdict


class EventBus:
    """事件总线"""
    _instance = None
    _handlers: Dict[str, List[Callable]] = defaultdict(list)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def on(self, event: str, handler: Callable):
        """订阅事件"""
        self._handlers[event].append(handler)
    
    def emit(self, event: str, data: Dict = None):
        """发布事件"""
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                print(f"事件处理失败: {e}")
    
    def off(self, event: str, handler: Callable = None):
        """取消订阅"""
        if handler:
            self._handlers[event].remove(handler)
        else:
            self._handlers[event] = []


event_bus = EventBus()
"""事件总线 - 事件驱动架构"""
from typing import Dict, List, Callable
from collections import defaultdict


class EventBus:
    """事件总线"""
    _instance = None
    _handlers: Dict[str, List[Callable]] = defaultdict(list)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def on(self, event: str, handler: Callable):
        """订阅事件"""
        self._handlers[event].append(handler)
    
    def emit(self, event: str, data: Dict = None):
        """发布事件"""
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
            except Exception as e:
                print(f"事件处理失败: {e}")
    
    def off(self, event: str, handler: Callable = None):
        """取消订阅"""
        if handler:
            self._handlers[event].remove(handler)
        else:
            self._handlers[event] = []


event_bus = EventBus()
