#!/usr/bin/env python3
import requests, json
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_URL = "http://localhost:11434/api/generate"
PORT = 8106

class ScriptHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/gen_script':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            topic = data.get('topic', 'AI工具')
            duration = data.get('duration', 3)
            
            prompt = f"""写一个{duration}分钟的YouTube视频脚本。主题：{topic}。

直接输出以下格式，不要有任何解释：

🎬 开场（15秒）：
[写一个吸引人的开场白]

🔥 工具1（30秒）：
名称：[名称]
亮点：[一句话]
场景：[怎么用]

🔥 工具2（30秒）：
同上

🔥 工具3-5（各30秒）：
同上

🎯 结尾（15秒）：
[总结 + 点赞关注引导]

要求：口语化，用"兄弟们"、"干货"等词。直接输出。"""

            resp = requests.post(OLLAMA_URL, json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 1500}
            }, timeout=60)
            
            if resp.status_code == 200:
                self.send_json({'success': True, 'script': resp.json().get('response', '')})
            else:
                self.send_json({'success': False, 'error': '生成失败'})
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    print(f"🎬 Script Generator on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), ScriptHandler).serve_forever()
