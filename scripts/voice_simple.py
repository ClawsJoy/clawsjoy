#!/usr/bin/env python3
"""简易语音交互"""
import os
import subprocess
import tempfile

from core.agents.builtin.personal_butler_v2 import PersonalButlerV2
user_id = os.environ.get("BUTLER_USER_ID", "john")
    personal_butler = PersonalButlerV2(user_id=user_id)

def listen():
    """录音识别"""
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    try:
        print("\n🎤 请说话... (3秒)", end='', flush=True)
        subprocess.run(['arecord', '-d', '3', '-f', 'cd', '-t', 'wav', '-q', temp_wav], check=True)
        print("\r🎤 识别中...", end='', flush=True)
        
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language='zh-CN')
            print(f"\r👤 你: {text}")
            return text
    except ImportError:
        print("\r❌ 请安装: pip install SpeechRecognition")
        return ""
    except Exception as e:
        print(f"\r❌ 识别失败: {e}")
        return ""
    finally:
        if os.path.exists(temp_wav):
            os.unlink(temp_wav)

def speak(text):
    """语音回复"""
    print(f"🤖 管家: {text}")
    try:
        temp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        subprocess.run(['edge-tts', '--text', text, '--voice', 'zh-CN-XiaoxiaoNeural', 
                        '--write-media', temp_mp3], check=True)
        subprocess.run(['ffplay', '-nodisp', '-autoexit', temp_mp3], capture_output=True)
        os.unlink(temp_mp3)
    except:
        pass

def main():
    print("\n=== 私人管家语音助手 ===\n")
    speak("你好，我是你的私人管家")
    
    while True:
        text = listen()
        if not text:
            continue
        if text in ["退出", "再见", "拜拜", "结束"]:
            speak("再见，随时为您服务")
            break
        result = personal_butler.process(text)
        speak(result.get('response', '抱歉，我没听清'))

if __name__ == "__main__":
    main()
