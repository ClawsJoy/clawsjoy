#!/usr/bin/env python3
"""私人管家语音助手 - 类高德地图体验"""
import os
import sys
import time
import tempfile
import subprocess
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.voice_service import voice_service
from core.agents.builtin.personal_butler_v2 import PersonalButlerV2
user_id = os.environ.get("BUTLER_USER_ID", "john")
    personal_butler = PersonalButlerV2(user_id=user_id)


class VoiceAssistant:
    """语音助手 - 唤醒词 + 连续对话"""
    
    # 唤醒词
    WAKE_WORDS = ["你好管家", "管家", "小管家", "嗨管家", "hey管家"]
    
    def __init__(self):
        self.butler = personal_butler
        self.is_listening = False
        self.conversation_mode = False  # 连续对话模式
        self.idle_count = 0
    
    def listen_once(self, timeout=5) -> str:
        """单次录音识别"""
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        
        try:
            subprocess.run(['arecord', '-d', str(timeout), '-f', 'cd', '-t', 'wav', '-q', temp_wav], 
                          capture_output=True, timeout=timeout+2)
            
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language='zh-CN')
                return text.lower()
        except:
            return ""
        finally:
            if os.path.exists(temp_wav):
                os.unlink(temp_wav)
    
    def detect_wake_word(self, text: str) -> bool:
        """检测唤醒词"""
        for word in self.WAKE_WORDS:
            if word in text:
                return True
        return False
    
    def speak(self, text: str):
        """语音回复"""
        print(f"🤖 管家: {text}")
        voice_service.speak(text)
    
    def process_command(self, text: str) -> bool:
        """处理命令，返回是否继续对话"""
        # 退出命令
        if any(word in text for word in ['退出', '再见', '拜拜', '结束']):
            self.speak("好的，随时唤醒我")
            self.conversation_mode = False
            return False
        
        # 进入连续对话模式
        if any(word in text for word in ['连续对话', '多轮对话', '继续聊']):
            self.speak("进入连续对话模式，直接说话即可")
            self.conversation_mode = True
            self.idle_count = 0
            return True
        
        # 退出连续对话
        if any(word in text for word in ['退出对话', '结束对话']):
            self.speak("退出连续对话模式")
            self.conversation_mode = False
            return False
        
        # 普通对话
        result = self.butler.process(text)
        response = result.get('response', '')
        if response:
            self.speak(response)
        
        return True
    
    def run(self):
        """主循环"""
        print("\n" + "=" * 50)
        print("🎙️ 私人管家语音助手")
        print("   唤醒词: '你好管家' 或 '管家'")
        print("   说 '连续对话' 进入多轮对话")
        print("   说 '退出' 结束")
        print("=" * 50 + "\n")
        
        # 启动提示音
        self.speak("你好，我是你的私人管家，叫我管家就可以唤醒我")
        
        while True:
            try:
                if self.conversation_mode:
                    # 连续对话模式：直接等待命令
                    print("🎤 请说话... (5秒超时)")
                    text = self.listen_once(timeout=5)
                    
                    if text:
                        print(f"👤 你: {text}")
                        self.process_command(text)
                        self.idle_count = 0
                    else:
                        self.idle_count += 1
                        if self.idle_count >= 3:
                            self.speak("长时间没有对话，退出连续对话模式")
                            self.conversation_mode = False
                            self.idle_count = 0
                else:
                    # 待机模式：等待唤醒词
                    print("💤 待机中... (说'你好管家'唤醒)")
                    text = self.listen_once(timeout=10)
                    
                    if text:
                        print(f"👤 检测到: {text}")
                        if self.detect_wake_word(text):
                            # 唤醒
                            self.speak("在的，请问有什么可以帮您？")
                            # 唤醒后立即进入服务模式
                            self.conversation_mode = True
                            self.idle_count = 0
                        else:
                            # 不是唤醒词，忽略
                            pass
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n👋 退出")
                break
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(1)


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
