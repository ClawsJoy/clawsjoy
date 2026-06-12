# core/agents/contracts/standard_json_contract.py

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class AgentCapability(Enum):
    """Agent 能力声明（编译时检查）"""
    CHAT = ("chat", "text")
    CODE = ("generate", "code")
    TRANSLATE = ("translate", "text")
    CALCULATE = ("calculate", "number")
    # ... 更多


@dataclass
class StandardJsonRequest:
    """标准化 JSON 请求（类型安全）"""
    version: str = "1.0"
    session_id: str = ""
    user_id: str = ""
    thread_id: str = ""
    turn: int = 0
    raw_input: str = ""
    action: str = ""
    target: str = ""
    keywords: list = None
    confidence: float = 0.95
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
    
    @classmethod
    def from_dict(cls, data: dict) -> "StandardJsonRequest":
        """从字典创建（带验证）"""
        return cls(
            version=data.get("version", "1.0"),
            session_id=data.get("session_id", ""),
            user_id=data.get("user_id", ""),
            thread_id=data.get("thread_id", ""),
            turn=data.get("turn", 0),
            raw_input=data.get("raw_input", ""),
            action=data.get("action", "chat"),
            target=data.get("target", "text"),
            keywords=data.get("keywords", []),
            confidence=data.get("confidence", 0.95)
        )


@dataclass
class StandardJsonResponse:
    """标准化 JSON 响应（类型安全）"""
    version: str = "1.0"
    session_id: str = ""
    user_id: str = ""
    thread_id: str = ""
    turn: int = 0
    raw_input: str = ""
    timestamp: str = ""
    action: str = ""
    target: str = ""
    keywords: list = None
    confidence: float = 0.95
    output_type: str = "text"
    output_content: str = ""
    output_data: dict = None
    status: str = "completed"
    next: str = "done"
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.output_data is None:
            self.output_data = {}
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "turn": self.turn,
            "raw_input": self.raw_input,
            "timestamp": self.timestamp,
            "action": self.action,
            "target": self.target,
            "keywords": self.keywords,
            "confidence": self.confidence,
            "output_type": self.output_type,
            "output_content": self.output_content,
            "output_data": self.output_data,
            "status": self.status,
            "next": self.next
        }


class StandardJsonCapable(ABC):
    """标准化 JSON 能力契约（接口）"""
    
    @abstractmethod
    def get_capabilities(self) -> list[AgentCapability]:
        """声明 Agent 的能力（编译时检查）"""
        pass
    
    @abstractmethod
    def execute_json(self, request: StandardJsonRequest) -> StandardJsonResponse:
        """执行标准化 JSON 请求"""
        pass
    
    def can_execute(self, action: str, target: str) -> tuple[bool, float]:
        """检查是否能执行（默认实现）"""
        for cap in self.get_capabilities():
            if cap.value[0] == action and cap.value[1] == target:
                return True, 0.95
        return False, 0.0


# 使用示例 - Agent 实现契约
class ChatAgent(BusinessAgent, StandardJsonCapable):
    
    def get_capabilities(self) -> list[AgentCapability]:
        return [AgentCapability.CHAT]
    
    def execute_json(self, request: StandardJsonRequest) -> StandardJsonResponse:
        # 类型安全的处理
        response_text = self._handle_chat(request.raw_input)
        
        return StandardJsonResponse(
            session_id=request.session_id,
            user_id=request.user_id,
            thread_id=request.thread_id,
            turn=request.turn + 1,
            raw_input=request.raw_input,
            action=request.action,
            target=request.target,
            keywords=request.keywords,
            output_content=response_text,
            status="completed"
        )
