#!/usr/bin/env python3
"""私人管家语音对话系统"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from lib.voice_service import voice_service
from core.agents.builtin.personal_butler_v2 import PersonalButlerV2
user_id = os.environ.get("BUTLER_USER_ID", "john")
    personal_butler = PersonalButlerV2(user_id=user_id)


class VoiceChat:
    """语音对话系统"""
    
    def __init__(self):
        self.butler = personal_butler
        self.stt_available = self._check_stt()
    
    def _check_stt(self):
        """检查语音识别是否可用"""
        try:
            import speech_recognition as sr
            return True
        except ImportError:
            print("⚠️ 语音识别未安装，将使用文字输入模式")
            return False
    
    def listen(self, timeout=5) -> str:
        """监听麦克风，识别语音"""
        if not self.stt_available:
            return input("👤 你: ")
        
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("🎤 请说话...", end='', flush=True)
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("\r🎤 识别中...", end='', flush=True)
                
                text = recognizer.recognize_google(audio, language='zh-CN')
                print(f"\r👤 你: {text}")
                return text
        except sr.WaitTimeoutError:
            print("\r⏰ 未检测到语音", end='')
            return ""
        except sr.UnknownValueError:
            print("\r❓ 无法识别", end='')
            return ""
        except Exception as e:
            print(f"\r❌ 识别失败: {e}")
            return ""
    
    def speak(self, text: str):
        """语音回复"""
        print(f"🤖 管家: {text}")
        voice_service.speak(text)
    
    def chat(self):
        """开始对话"""
        print("\n" + "=" * 40)
        print("🎙️ 私人管家语音助手")
        print("   说 '退出' 或 '再见' 结束对话")
        print("=" * 40 + "\n")
        
        # 主动问候
        greeting = self.butler.active_greeting()
        if greeting:
            self.speak(greeting)
        
        while True:
            # 监听用户输入
            user_text = self.listen(timeout=10)
            
            if not user_text:
                continue
            
            # 检查退出
            if any(word in user_text for word in ['退出', '再见', '拜拜', 'exit', 'quit']):
                self.speak("再见，随时为您服务")
                break
            
            # 处理消息
            result = self.butler.process(user_text)
            response = result.get('response', '抱歉，我没理解您的意思')
            
            # 语音回复
            self.speak(response)
            
            # 主动服务（可选）
            active_msg = self.butler.get_active_message()
            if active_msg:
                self.speak(active_msg)
    
    def text_mode(self):
        """文字模式（备用）"""
        print("\n📝 文字对话模式（输入 exit 退出）\n")
        while True:
            user_text = input("👤 你: ").strip()
            if user_text.lower() in ['exit', '退出', 'quit']:
                print("👋 再见")
                break
            if not user_text:
                continue
            result = self.butler.process(user_text)
            print(f"🤖 管家: {result.get('response', '')}\n")


if __name__ == "__main__":
    chat = VoiceChat()
    
    # 检查麦克风
    if chat.stt_available:
        try:
            chat.chat()
        except Exception as e:
            print(f"语音模式失败: {e}")
            print("切换到文字模式...")
            chat.text_mode()
    else:
        chat.text_mode()
