"""Agent 类型定义"""

from typing import TypedDict, List, Optional
from datetime import datetime

class AgentStats(TypedDict):
    """Agent 统计信息"""
    tasks_handled: int
    success_count: int
    fail_count: int
    total_response_time: float
    learning_count: int

class Experience(TypedDict):
    """经验记录"""
    timestamp: datetime
    task: str
    result: str
    lesson: Optional[str]
