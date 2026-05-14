#!/usr/bin/env python3
"""Chat API - 硬路由模式（不经过大模型判断）"""

import json
import sys
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, '/mnt/d/clawsjoy/agents')
from tenant_agent import TenantAgent

PORT = 18109

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
        tenant_id = data.get('tenant_id', 'tenant_1')
        
        agent = TenantAgent(tenant_id)
        user_lower = user_input.lower()
        
        print(f"📥 收到: {user_input[:50]}...")
        
        # ========== 硬路由（不依赖大模型）==========
        
        # 1. 生成并上传
        if ("生成" in user_lower or "制作" in user_lower) and ("上传" in user_lower or "发布" in user_lower):
            print("🎬 路由: 生成并上传")
            # 提取城市
            topic = "香港"
            for city in ["香港", "上海", "深圳", "北京", "广州", "杭州"]:
                if city in user_input:
                    topic = city
                    break
            result = agent.generate_and_upload_async(topic, 30, 15)
            self._send_json({"type": "result", "message": result.get("message", "完成"), "data": result})
            return
        
        # 2. 仅上传
        if "上传" in user_lower and ("youtube" in user_lower or "视频" in user_lower):
            print("📤 路由: 仅上传")
            result = agent.upload_to_youtube()
            self._send_json({"type": "result", "message": result.get("message", "上传完成"), "data": result})
            return
        
        # 3. 仅生成
        if ("生成" in user_lower or "制作" in user_lower) and "上传" not in user_lower:
            print("🎬 路由: 仅生成")
            topic = "香港"
            for city in ["香港", "上海", "深圳", "北京", "广州", "杭州"]:
                if city in user_input:
                    topic = city
                    break
            result = agent.generate_video_only(user_input)
            self._send_json({"type": "result", "message": result.get("message", "生成完成"), "data": result})
            return
        
        # 4. 配置告警
        if ("告警" in user_lower or "webhook" in user_lower) and ("配置" in user_lower or "设置" in user_lower):
            print("🔔 路由: 配置告警")
            url_match = re.search(r'https?://[^\s]+', user_input)
            if url_match:
                platform = "dingtalk"
                if "飞书" in user_input:
                    platform = "feishu"
                elif "企微" in user_input:
                    platform = "wechat"
                result = agent.set_alert_webhook(platform, url_match.group())
                self._send_json({"type": "result", "message": f"✅ 已配置 {platform} 告警", "data": result})
            else:
                self._send_json({"type": "text", "message": "请提供 Webhook URL"})
            return
        
        # 5. 普通对话（调用大模型）
        print("💬 路由: 普通对话")
        try:
            import requests
            resp = requests.post("http://localhost:11434/api/generate", json={
                "model": "qwen2.5:3b",
                "prompt": user_input,
                "stream": False,
                "options": {"num_predict": 500}
            }, timeout=60)
            if resp.status_code == 200:
                reply = resp.json().get("response", "")
                self._send_json({"type": "text", "message": reply})
            else:
                self._send_json({"type": "text", "message": "服务暂时不可用"})
        except Exception as e:
            self._send_json({"type": "text", "message": f"服务异常: {str(e)}"})
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    print(f"🤖 Chat API (硬路由模式) 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

# 在生成并上传的路由中添加时间提取
import re

def extract_delay_minutes(user_input):
    """从用户输入中提取延迟分钟数"""
    # 匹配 "X分钟后"、"X分钟"、"推迟X分钟"、"延迟X分钟"
    patterns = [
        r'(\d+)\s*分钟后',
        r'(\d+)\s*分钟',
        r'推迟\s*(\d+)\s*分钟',
        r'延迟\s*(\d+)\s*分钟',
    ]
    for pattern in patterns:
        match = re.search(pattern, user_input)
        if match:
            return int(match.group(1))
    return None  # 默认使用全局配置

def extract_delay(user_input):
    import re
    patterns = [r'(\d+)\s*分钟后', r'(\d+)\s*分钟']
    for p in patterns:
        m = re.search(p, user_input)
        if m:
            return int(m.group(1))
    return None  # 默认

# 在路由中替换
# delay = extract_delay(user_input) or 15
# result = agent.generate_and_upload_async(topic, 30, delay)
