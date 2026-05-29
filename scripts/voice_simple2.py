#!/usr/bin/env python3
"""语音交互 - 使用 parec 录音"""
import subprocess
import tempfile
import os

from core.agents.builtin.personal_butler_v2 import PersonalButlerV2
user_id = os.environ.get("BUTLER_USER_ID", "john")
    personal_butler = PersonalButlerV2(user_id=user_id)

def listen():
    """录音识别"""
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    
    try:
        print("\n🎤 请说话... (3秒)", end='', flush=True)
        # 使用 parec 录音
        cmd = f'parec --format=s16le --channels=1 --rate=16000 --latency=5 | sox -t raw -r 16000 -e signed -b 16 -c 1 - {temp_wav}'
        subprocess.run(cmd, shell=True, timeout=4)
        print("\r🎤 识别中...", end='', flush=True)
        
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language='zh-CN')
            print(f"\r👤 你: {text}")
            return text
    except Exception as e:
        print(f"\r❌ 识别失败: {e}")
        return ""
    finally:
        if os.path.exists(temp_wav):
            os.unlink(temp_wav)

def speak(text):
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
        if text in ["退出", "再见", "拜拜"]:
            speak("再见，随时为您服务")
            break
        result = personal_butler.process(text)
        speak(result.get('response', '抱歉，我没听清'))

if __name__ == "__main__":
    main()
