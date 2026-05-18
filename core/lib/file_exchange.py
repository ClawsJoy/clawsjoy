#!/usr/bin/env python3
"""异步文件夹交割通信"""

import json
import uuid
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    HIGH = 0
    NORMAL = 1
    LOW = 2


class FileExchange:
    def __init__(self, exchange_dir: str = "data/exchange"):
        self.exchange_dir = Path(exchange_dir)
        self._init_dirs()
        self.handlers: Dict[str, Callable] = {}
        self._listener_thread = None
        self._running = False
    
    def _init_dirs(self):
        self.dirs = {
            "incoming": self.exchange_dir / "incoming",
            "to_decision": self.exchange_dir / "to_decision",
            "to_chat": self.exchange_dir / "to_chat",
            "to_executor": self.exchange_dir / "to_executor",
            "processing": self.exchange_dir / "processing",
            "done": self.exchange_dir / "done",
            "urgent": self.exchange_dir / "urgent",
        }
        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)
    
    def send(self, to_agent: str, data: Dict, priority: MessagePriority = MessagePriority.NORMAL) -> str:
        message_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
        
        target_dir = {
            "decision": self.dirs["to_decision"],
            "chat": self.dirs["to_chat"],
            "executor": self.dirs["to_executor"],
        }.get(to_agent, self.dirs["incoming"])
        
        if priority == MessagePriority.HIGH:
            target_dir = self.dirs["urgent"]
        
        message = {
            "id": message_id,
            "from": data.get("from", "unknown"),
            "to": to_agent,
            "action": data.get("action"),
            "data": data.get("data", {}),
            "priority": priority.value,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        file_path = target_dir / message_id
        with open(file_path, 'w') as f:
            json.dump(message, f, indent=2)
        
        logger.info(f"📨 发送消息 {message_id} → {to_agent}")
        return message_id
    
    def receive(self, agent_name: str) -> Optional[Dict]:
        """接收发给自己的消息"""
        target_dir = self.dirs.get(f"to_{agent_name}", self.dirs["incoming"])
        
        for file_path in list(target_dir.glob("*.json")):
            try:
                with open(file_path, 'r') as f:
                    message = json.load(f)
                
                if message.get("to") == agent_name:
                    shutil.move(str(file_path), str(self.dirs["processing"] / file_path.name))
                    logger.info(f"📬 {agent_name} 收到消息: {message.get('id')}")
                    return message
            except Exception as e:
                logger.error(f"读取消息失败: {e}")
        
        return None
    
    def ack(self, message_id: str, result: Dict):
        """确认处理完成"""
        for src_dir in [self.dirs["processing"], self.dirs["urgent"], self.dirs["incoming"]]:
            src = src_dir / message_id
            if src.exists():
                dst = self.dirs["done"] / message_id
                with open(src, 'r') as f:
                    message = json.load(f)
                message["status"] = "done"
                message["result"] = result
                message["completed_at"] = datetime.now().isoformat()
                with open(src, 'w') as f:
                    json.dump(message, f, indent=2)
                shutil.move(str(src), str(dst))
                logger.info(f"✅ 消息完成 {message_id}")
                return
        
        logger.warning(f"未找到消息 {message_id}")
    
    def get_stats(self) -> Dict:
        return {
            "incoming": len(list(self.dirs["incoming"].glob("*.json"))),
            "to_decision": len(list(self.dirs["to_decision"].glob("*.json"))),
            "to_chat": len(list(self.dirs["to_chat"].glob("*.json"))),
            "to_executor": len(list(self.dirs["to_executor"].glob("*.json"))),
            "processing": len(list(self.dirs["processing"].glob("*.json"))),
            "done": len(list(self.dirs["done"].glob("*.json"))),
            "urgent": len(list(self.dirs["urgent"].glob("*.json"))),
        }


file_exchange = FileExchange()


if __name__ == "__main__":
    print("测试文件交换")
    msg_id = file_exchange.send("decision", {"from": "test", "action": "test", "data": {"msg": "hello"}})
    print(f"发送: {msg_id}")
    print(f"统计: {file_exchange.get_stats()}")
    
    # 测试接收
    msg = file_exchange.receive("decision")
    if msg:
        print(f"收到: {msg.get('id')}")

    def receive_safe(self, agent_name: str) -> Optional[Dict]:
        """安全接收消息（带安全检查）"""
        from lib.security_hook import security_hook
        
        message = self.receive(agent_name)
        if message:
            # 安全检查
            safe, error_response = security_hook.check_message(message)
            if not safe:
                logger.warning(f"消息被安全拦截: {error_response}")
                # 返回错误响应
                return {
                    "action": "security_error",
                    "error": error_response,
                    "original_message": message
                }
        return message
