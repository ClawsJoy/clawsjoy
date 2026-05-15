#!/usr/bin/env python3
"""Chat API - 集成关键词自动学习 + Meilisearch"""

import json
import requests
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/mnt/d/clawsjoy/agents')
try:
    from keyword_learner import KeywordLearner
    keyword_learner = KeywordLearner()
except ImportError:
    keyword_learner = None
    print("⚠️ KeywordLearner 未找到")

PORT = 18109
for i, arg in enumerate(sys.argv):
    if arg == "--port" and i+1 < len(sys.argv):
        PORT = int(sys.argv[i+1])

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

def search_keywords(query):
    try:
        resp = requests.post("http://localhost:7700/indexes/keywords/search",
                             json={"q": query, "limit": 3}, timeout=2)
        if resp.status_code == 200:
            return [h["name"] for h in resp.json().get("hits", []) if h.get("name")]
    except:
        pass
    return []

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/agent':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        user_input = data.get('text', data.get('message', ''))

        # 🔍 关键词自动学习
        if keyword_learner:
            learned = keyword_learner.process_user_input(user_input)
            if learned.get('learned'):
                print(f"📚 自动学习新关键词: {learned['learned']}")
                # 同步到 Meilisearch
                keyword_learner.sync_to_meilisearch()

        # 🔍 关键词增强
        keywords = search_keywords(user_input)
        enhanced_prompt = user_input
        if keywords:
            enhanced_prompt = f"{user_input}\n[相关关键词: {', '.join(keywords)}]"
            print(f"🔍 关键词增强: {keywords}")

        try:
            resp = requests.post(OLLAMA_API, json={
                "model": OLLAMA_MODEL,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {"num_predict": 500, "temperature": 0.7}
            }, timeout=60)
            if resp.status_code == 200:
                reply = resp.json().get('response', '')
                self._send_json({'type': 'text', 'message': reply})
            else:
                self._send_json({'type': 'text', 'message': '服务暂时不可用'})
        except Exception as e:
            self._send_json({'type': 'text', 'message': f'服务异常: {str(e)}'})

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    print(f"🤖 Chat API (集成关键词学习) 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

# ========== 脱敏钩子（可选，增加安全边界）==========
# 注意：这个钩子是为了防止直接调用 Chat API 时泄露
# 真正的安全边界在 TenantAgent 层

def sanitize_for_model(text):
    """在进入大模型前最后一道防线"""
    patterns = [
        (r'client_secret["\s:]+["\']?([a-zA-Z0-9_\-]{10,})', '[SECRET]'),
        (r'api_key["\s:]+["\']?([a-zA-Z0-9_\-]{10,})', '[API_KEY]'),
        (r'access_token["\s:]+["\']?([a-zA-Z0-9_\-\.]{20,})', '[TOKEN]'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

# 在 _handle_agent 中调用
# 找到 user_input = data.get('text', '') 这一行
# 在后面加一行：user_input = sanitize_for_model(user_input)

# ========== YouTube 意图识别 ==========
def detect_youtube_intent(user_input, tenant_id="tenant_1"):
    user_lower = user_input.lower()
    agent = get_agent(tenant_id)
    
    # 配置 YouTube
    if "配置 youtube" in user_lower or "配置油管" in user_lower or "youtube 授权" in user_lower:
        result = agent.setup_youtube(user_input)
        if result.get("action") == "ask_secrets":
            return {"type": "text", "message": result["message"]}
        return {"type": "text", "message": result["message"]}
    
    # 上传视频
    if "上传" in user_lower and ("youtube" in user_lower or "油管" in user_lower or "视频" in user_lower):
        result = agent.upload_to_youtube()
        return {"type": "text", "message": result["message"]}
    
    return None

# 在 do_POST 的意图识别部分添加
# 在 detect_intent 调用后，添加：
# youtube_result = detect_youtube_intent(user_input, tenant_id)
# if youtube_result:
#     self._send_json(youtube_result)
#     return
