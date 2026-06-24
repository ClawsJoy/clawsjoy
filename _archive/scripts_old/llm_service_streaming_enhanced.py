#!/usr/bin/env python3
"""增强版流式 LLM 服务 - 支持 SSE + 缓存 + 记忆"""

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import json
import logging
import time
from collections import OrderedDict
from threading import Lock

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL = "qwen2.5:3b"

# 简单缓存
class ResponseCache:
    def __init__(self, ttl=300, max_size=100):
        self.cache = OrderedDict()
        self.ttl = ttl
        self.max_size = max_size
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    self.cache.move_to_end(key)
                    return value
                else:
                    del self.cache[key]
            return None

    def set(self, key, value):
        with self.lock:
            self.cache[key] = (value, time.time())
            self.cache.move_to_end(key)
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

cache = ResponseCache()

@app.route("/chat", methods=["POST"])
def chat():
    """阻塞式接口（兼容现有系统）"""
    data = request.json
    message = data.get("message", "")

    # 检查缓存
    cached = cache.get(message)
    if cached:
        logger.info(f"缓存命中: {message[:30]}")
        return jsonify({"response": cached, "success": True, "cached": True})

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL, "prompt": message, "stream": False},
            timeout=60
        )

        if resp.status_code == 200:
            result = resp.json()
            response = result.get("response", "")
            cache.set(message, response)
            return jsonify({"response": response, "success": True})
        else:
            return jsonify({"response": f"错误: {resp.status_code}", "success": False}), 500
    except Exception as e:
        return jsonify({"response": str(e), "success": False}), 500

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """流式接口 SSE - 支持缓存和实时输出"""
    data = request.json
    message = data.get("message", "")

    # 检查缓存（流式也支持缓存）
    cached = cache.get(message)
    if cached:
        logger.info(f"流式缓存命中: {message[:30]}")
        def cached_generate():
            yield f"data: {json.dumps({'token': cached, 'cached': True})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        return Response(cached_generate(), mimetype='text/event-stream')

    def generate():
        try:
            start_time = time.time()
            first_token_time = None
            full_response = []

            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": MODEL, "prompt": message, "stream": True},
                timeout=60,
                stream=True
            )

            for line in resp.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)

                        # 记录首字时间
                        if 'response' in chunk and chunk['response'] and first_token_time is None:
                            first_token_time = time.time()
                            logger.info(f"首字延迟: {(first_token_time - start_time)*1000:.0f}ms")

                        if 'response' in chunk and chunk['response']:
                            token = chunk['response']
                            full_response.append(token)
                            yield f"data: {json.dumps({'token': token})}\n\n"

                        if chunk.get('done'):
                            # 保存到缓存
                            complete_response = ''.join(full_response)
                            if complete_response:
                                cache.set(message, complete_response)

                            total_time = time.time() - start_time
                            logger.info(f"流式完成: {total_time*1000:.0f}ms, 长度: {len(complete_response)}")
                            yield f"data: {json.dumps({'done': True, 'total_time': total_time})}\n\n"
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            logger.error(f"流式错误: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": MODEL,
        "streaming": True,
        "cache_size": len(cache.cache)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False, threaded=True)
