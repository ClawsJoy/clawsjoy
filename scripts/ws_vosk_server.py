#!/usr/bin/env python3
#!/usr/bin/env python3
"""Ws Vosk Server - Ws Vosk Server 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""
import asyncio
import json
from pathlib import Path

import numpy as np
import websockets
from vosk import KaldiRecognizer, Model

MODEL_PATH = Path("models/vosk/small")
if not MODEL_PATH.exists():
    print(f"❌ 模型不存在: {MODEL_PATH}")
    exit(1)

print(f"✅ 加载模型: {MODEL_PATH}")
model = Model(str(MODEL_PATH))


async def voice_handler(websocket):
    print(f"🔊 客户端连接")
    recognizer = KaldiRecognizer(model, 16000)

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                recognizer.AcceptWaveform(message)
                partial = json.loads(recognizer.PartialResult())
                if partial.get("partial"):
                    print(f"📝 Partial: {partial['partial']}")
                    await websocket.send(
                        json.dumps({"type": "partial", "text": partial["partial"]})
                    )
            else:
                print(f"📨 控制消息: {message}")
    except Exception as e:
        print(f"❌ 错误: {e}")


async def main():
    print("=" * 50)
    print("🎤 Vosk WebSocket 语音识别服务")
    print("=" * 50)
    print(f"📡 WebSocket: ws://localhost:5005")
    print("=" * 50)
    async with websockets.serve(voice_handler, "0.0.0.0", 5005):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
