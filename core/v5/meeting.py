"""会议系统 - 多 Agent 协作会议"""

from typing import Dict, List
import uuid
import time


class MeetingRoom:
    """会议室"""
    
    def __init__(self, meeting_id: str, topic: str, participants: List[str]):
        self.meeting_id = meeting_id
        self.topic = topic
        self.participants = participants
        self.messages: List[Dict] = []
        self.created_at = time.time()
        self.status = "active"
    
    def add_message(self, from_agent: str, content: str):
        """添加消息"""
        self.messages.append({
            "from": from_agent,
            "content": content,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> str:
        """获取会议摘要"""
        if not self.messages:
            return f"会议 '{self.topic}' 暂无讨论内容"
        
        summary = f"会议: {self.topic}\n"
        summary += f"参与者: {', '.join(self.participants)}\n"
        summary += f"消息数: {len(self.messages)}\n"
        return summary


class MeetingManager:
    """会议管理器"""
    
    def __init__(self):
        self.meetings: Dict[str, MeetingRoom] = {}
    
    def create_meeting(self, topic: str, participants: List[str]) -> str:
        """创建会议"""
        meeting_id = str(uuid.uuid4())[:8]
        self.meetings[meeting_id] = MeetingRoom(meeting_id, topic, participants)
        print(f"   📅 创建会议: {topic} (ID: {meeting_id})")
        return meeting_id
    
    def join_meeting(self, meeting_id: str, agent_name: str) -> bool:
        """加入会议"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False
        
        if agent_name not in meeting.participants:
            meeting.participants.append(agent_name)
        return True
    
    def speak(self, meeting_id: str, from_agent: str, content: str) -> bool:
        """发言"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False
        
        meeting.add_message(from_agent, content)
        return True
    
    def get_summary(self, meeting_id: str) -> Dict:
        """获取会议信息"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return {"error": "会议不存在"}
        
        return {
            "meeting_id": meeting.meeting_id,
            "topic": meeting.topic,
            "participants": meeting.participants,
            "messages": meeting.messages,
            "summary": meeting.get_summary()
        }
    
    def close_meeting(self, meeting_id: str) -> bool:
        """关闭会议"""
        if meeting_id in self.meetings:
            self.meetings[meeting_id].status = "closed"
            return True
        return False


meeting_manager = MeetingManager()
