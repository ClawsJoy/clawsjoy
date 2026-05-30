#!/usr/bin/env python3
"""Event Bus - Event Bus 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from typing import Dict, List, Callable, Any
from collections import defaultdict


class EventBus:
    """事件总线 - 单例模式，支持灵活 handler 签名"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers: Dict[str, List[Callable]] = defaultdict(list)
        return cls._instance
    
    def on(self, event: str, handler: Callable) -> Dict:
        """订阅事件（避免重复订阅）"""
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)
    
    def subscribe(self, event: str, handler: Callable) -> Dict:
        """订阅事件（on 的别名）"""
        self.on(event, handler)
    
    def emit(self, event: str, data: Any = None) -> Dict:
        """触发事件 - 支持 0/1/2 参数的 handler"""
        for handler in self._handlers.get(event, []):
            try:
                handler(event, data)
            except TypeError:
                try:
                    handler(event)
                except TypeError:
                    try:
                        handler()
                    except TypeError:
                        pass
    
    def publish(self, event: str, data: Any = None) -> Dict:
        """发布事件（emit 的别名）"""
        self.emit(event, data)
    
    def off(self, event: str, handler: Callable = None) -> Dict:
        """取消订阅"""
        if handler is None:
            self._handlers[event] = []
        elif handler in self._handlers[event]:
            self._handlers[event].remove(handler)


# 全局单例
event_bus = EventBus()
