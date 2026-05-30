#!/usr/bin/env python3
"""ClawsJoy 移动端服务 - 集成真实 chat_agent"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import tempfile
import threading
import asyncio
import subprocess
from datetime import datetime

app = Flask(__name__, static_folder='web', static_url_path='/static')
CORS(app)

print("=" * 60)
print("🚀 ClawsJoy 移动端服务 v7")
print("=" * 60)

# ========== TTS（Edge TTS / eSpeak）==========


class SimpleTTS:
    def __init__(self):
        self.enabled = True
        print("✅ TTS: eSpeak 已启用")
    
    def speak(self, text):
        if not text:
            return False
        
        def _speak():
            import subprocess
            subprocess.run(['espeak', '-v', 'zh', '-s', '130', text], capture_output=True)
        
        import threading
        threading.Thread(target=_speak, daemon=True).start()
        return True




tts = SimpleTTS()

# ========== VOSK 初始化 ==========
VOSK_AVAILABLE = False
vosk_model = None

try:
    import vosk
    import wave
    
    for model_path in ["vosk-model-small-cn-0.22"]:
        if os.path.exists(model_path):
            vosk_model = vosk.Model(model_path)
            VOSK_AVAILABLE = True
            print(f"✅ VOSK 模型已加载")
            break
except ImportError:
    print("⚠️ VOSK 未安装")

print(f"🎤 语音识别: {'已启用' if VOSK_AVAILABLE else '未启用'}")
print("=" * 60)

# ========== 静态路由 ==========
@app.route('/')
@app.route('/mobile/')
@app.route('/mobile/<path:filename>')
def mobile_pages(filename='index_complete.html'):
    try:
        return send_from_directory('web/mobile', filename)
    except:
        return send_from_directory('web/mobile', 'index.html')

# ========== API 路由 ==========
@app.route('/api/voice/status', methods=['GET'])
def voice_status():
    return jsonify({
        'tts_enabled': tts.enabled,
        'stt_enabled': VOSK_AVAILABLE,
        'vosk_available': VOSK_AVAILABLE,
        'model_loaded': vosk_model is not None
    })

@app.route('/api/vosk/status', methods=['GET'])
def vosk_status():
    return jsonify({'available': VOSK_AVAILABLE, 'model_loaded': vosk_model is not None})

@app.route('/api/voice/recognize', methods=['POST'])
@app.route('/api/vosk/recognize', methods=['POST'])
def recognize():
    if not VOSK_AVAILABLE or not vosk_model:
        return jsonify({'status': 'error', 'message': 'VOSK not available'}), 503
    
    try:
        import wave
        
        if 'audio' not in request.files:
            return jsonify({'status': 'error', 'message': 'No audio file'}), 400
        
        audio_file = request.files['audio']
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.save(temp_file.name)
        
        wf = wave.open(temp_file.name, 'rb')
        rec = vosk.KaldiRecognizer(vosk_model, wf.getframerate())
        
        text_parts = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get('text'):
                    text_parts.append(result['text'])
        
        final = json.loads(rec.FinalResult())
        if final.get('text'):
            text_parts.append(final['text'])
        
        wf.close()
        os.unlink(temp_file.name)
        
        recognized_text = ' '.join(text_parts)
        return jsonify({'status': 'success', 'text': recognized_text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    """调用真正的 chat_agent"""
    try:
        from agents.chat_agent.agent import ChatAgent
        
        data = request.json
        message = data.get('message', '')
        user_id = data.get('user_id', 'mobile_user')
        
        if not message:
            return jsonify({'response': '请输入内容'}), 400
        
        # 调用 chat_agent 处理
        result = chat_agent.process(message, {'user_id': user_id})
        reply = result.get('response', '处理完成')
        
        # 自动 TTS 播报
        if reply and len(reply) < 200:
            tts.speak(reply)
        
        return jsonify({'response': reply})
        
    except Exception as e:
        print(f"Chat Agent 错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'response': f"处理出错: {str(e)}"}), 500

@app.route('/api/tts/speak', methods=['POST'])
def tts_speak():
    if not tts.enabled:
        return jsonify({'status': 'error', 'message': 'TTS not available'}), 503
    
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({'status': 'error', 'message': 'No text'}), 400
        
        tts.speak(text)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'tts': tts.enabled,
        'stt': VOSK_AVAILABLE
    })

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("✅ 服务启动")
    print(f"📍 http://localhost:5003/mobile/")
    print(f"📝 Chat Agent: 已集成")
    print("=" * 60 + "\n")
    app.run(host='0.0.0.0', port=5003, debug=False, use_reloader=False)
