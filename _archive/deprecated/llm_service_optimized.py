#!/usr/bin/env python3
"""LLM 服务 - 增强版（创意+数学）"""

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import json
import logging
import time
import re
from collections import OrderedDict
from threading import Lock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lib.advanced_math_solver import math_solver
from core.lib.creative_writer import creative_writer

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL = "qwen2.5:3b"

# 增强版系统提示词
SYSTEM_PROMPT = """你是 ClawsJoy，一个智能助手。

能力范围：
1. 数学计算 - 准确计算并给出步骤
2. 逻辑推理 - 严谨推理
3. 代码生成 - 高质量代码
4. 创意写作 - 生动有趣的故事和诗歌
5. 对话记忆 - 记住用户偏好

创作要求：
- 故事要有悬念和反转
- 诗歌要押韵优美
- 回答要完整不截断

数学要求：
- 逐步推导
- 给出最终数字答案"""

class ResponseCache:
    def __init__(self, ttl=300, max_size=200):
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

# 问题类型识别
def detect_question_type(question: str) -> str:
    """识别问题类型"""
    if any(kw in question for kw in ['故事', '小说', '童话', '寓言']):
        return 'story'
    if any(kw in question for kw in ['诗', '诗歌', '绝句', '词']):
        return 'poetry'
    if any(kw in question for kw in ['进水', '出水', '合作', '效率']):
        return 'math'
    return 'general'

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    
    # 检查缓存
    cached = cache.get(message)
    if cached:
        logger.info(f"缓存命中: {message[:30]}")
        return jsonify({"response": cached, "success": True, "cached": True})
    
    # 识别问题类型
    qtype = detect_question_type(message)
    logger.info(f"问题类型: {qtype}")
    
    # 数学问题特殊处理
    if qtype == 'math':
        # 工作效率问题
        result = math_solver.solve_work_problem(message)
        if result:
            cache.set(message, result)
            return jsonify({"response": result, "success": True, "math": True})
        
        # 百分比问题
        result = math_solver.solve_percentage(message)
        if result:
            cache.set(message, result)
            return jsonify({"response": result, "success": True, "math": True})
    
    # 创意写作特殊处理
    enhanced_prompt = SYSTEM_PROMPT
    if qtype == 'story':
        enhanced_prompt = creative_writer.enhance_story_prompt(message)
    elif qtype == 'poetry':
        enhanced_prompt = creative_writer.enhance_poetry_prompt('五言绝句', message)
    else:
        enhanced_prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n请回答："
    
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7 if qtype in ['story', 'poetry'] else 0.3,
                    "num_predict": 2048,
                    "top_p": 0.9
                }
            },
            timeout=120
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
    """流式接口"""
    data = request.json
    message = data.get("message", "")
    
    cached = cache.get(message)
    if cached:
        def gen():
            yield f"data: {json.dumps({'token': cached, 'cached': True})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        return Response(gen(), mimetype='text/event-stream')
    
    qtype = detect_question_type(message)
    enhanced_prompt = SYSTEM_PROMPT
    if qtype == 'story':
        enhanced_prompt = creative_writer.enhance_story_prompt(message)
    
    def generate():
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": MODEL,
                    "prompt": enhanced_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7 if qtype == 'story' else 0.3,
                        "num_predict": 2048
                    }
                },
                timeout=120,
                stream=True
            )
            
            full = []
            for line in resp.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if 'response' in chunk and chunk['response']:
                            token = chunk['response']
                            full.append(token)
                            yield f"data: {json.dumps({'token': token})}\n\n"
                        if chunk.get('done'):
                            complete = ''.join(full)
                            if complete:
                                cache.set(message, complete)
                            yield f"data: {json.dumps({'done': True})}\n\n"
                    except:
                        pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"model": MODEL, "status": "ok", "cache_size": len(cache.cache)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False, threaded=True)

# 导入工具模块
from core.lib.tools import tool_manager
from core.lib.knowledge_base import knowledge_base

# 在 chat 函数中添加工具处理
def handle_tools(message: str) -> Optional[str]:
    """处理工具调用"""
    # 时间查询
    if any(kw in message for kw in ['时间', '几点', '日期']):
        return tool_manager.get_current_time()
    
    # 简单计算
    calc_match = re.search(r'(\d+[\+\-\*\/]\d+)', message)
    if calc_match:
        result = tool_manager.calculate(calc_match.group(1))
        if result:
            return result
    
    # 知识查询
    if message.startswith('什么是') or message.startswith('解释'):
        topic = message.replace('什么是', '').replace('解释', '').strip()[:20]
        knowledge = knowledge_base.get(topic)
        if knowledge:
            return knowledge
    
    return None
