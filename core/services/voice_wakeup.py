"""语音唤醒服务 - 简易版"""

import threading
import time
from pathlib import Path
from typing import Dict, Optional, Callable


class VoiceWakeup:
    """语音唤醒检测"""

    def __init__(self):
        self.wake_words = ["小管", "你好小管", "clawsjoy", "嘿小管"]
        self.listeners = []
        self.running = False
        print("🎤 语音唤醒服务已初始化")

    def add_listener(self, callback: Callable):
        """添加唤醒监听器"""
        self.listeners.append(callback)

    def detect(self, text: str) -> bool:
        """检测唤醒词"""
        text_lower = text.lower()
        for word in self.wake_words:
            if word in text_lower:
                print(f"🎯 检测到唤醒词: {word}")
                for callback in self.listeners:
                    callback(text)
                return True
        return False

    def start(self):
        """启动服务（后台监听）"""
        self.running = True
        print("🎤 语音唤醒服务已启动")
        print(f"   唤醒词: {self.wake_words}")

    def stop(self):
        self.running = False


voice_wakeup = VoiceWakeup()
