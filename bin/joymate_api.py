#!/usr/bin/env python3
"""Joy Mate 后端 API 服务。

聚合记忆检索、任务查询/提交、技能列表与记忆写入能力。
"""

import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from settings import CLAWSJOY_ROOT, TENANTS_DIR, SKILLS_DIR, TASK_QUEUE_DIR, PORT_JOYMATE
from py_logging import get_logger

TENANTS_ROOT = TENANTS_DIR
LOGGER = get_logger("joymate_api")

def retrieve_memory(tenant_id, query):
    """从租户记忆文档中做轻量关键词匹配检索。"""
    memory_path = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / "main" / "evolution" / "LEARNINGS.md"
    if not memory_path.exists():
        return None
    
    content = memory_path.read_text(encoding='utf-8')
    # 简单关键词匹配：按字符过滤后在分段文本中查找。
    keywords = [w for w in query if w.isalnum() and len(w) > 1]
    sections = content.split('\n## ')
    
    for sec in sections:
        for kw in keywords:
            if kw in sec:
                return sec[:500]
    return None

class JoyMateHandler(BaseHTTPRequestHandler):
    """Joy Mate API 请求处理器。"""

    def do_GET(self):
        """处理记忆检索、任务列表与技能列表查询接口。"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/memory/retrieve':
            params = parse_qs(parsed.query)
            tenant_id = int(params.get('tenant_id', ['1'])[0])
            query = params.get('query', [''])[0]
            
            context = retrieve_memory(tenant_id, query)
            self.send_json({'context': context})
        
        elif path == '/api/tasks':
            # 从临时队列目录读取待处理任务（用于前端展示）。
            tenant_id = int(parsed.query.split('=')[1]) if 'tenant_id' in parsed.query else 1
            tasks_dir = TASK_QUEUE_DIR
            tasks = []
            if tasks_dir.exists():
                for f in tasks_dir.glob("*.json"):
                    try:
                        task = json.loads(f.read_text())
                        tasks.append(task)
                    except:
                        pass
            self.send_json(tasks)
        
        elif path == '/api/skills':
            skills_dir = SKILLS_DIR
            skills = []
            if skills_dir.exists():
                for f in skills_dir.glob("*.md"):
                    skills.append({"name": f.stem, "file": str(f)})
            self.send_json(skills)
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理任务提交与记忆写入接口。"""
        if self.path == '/api/task/submit':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            task_file = TASK_QUEUE_DIR / f"task_{data.get('type', 'unknown')}.json"
            task_file.parent.mkdir(parents=True, exist_ok=True)
            task_file.write_text(json.dumps(data, indent=2))
            self.send_json({'success': True, 'task_id': task_file.name})
        
        elif self.path == '/api/memory/record':
            # 以追加方式写入 LEARNINGS.md，保留历史演化记录。
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            tenant_id = data.get('tenant_id', 1)
            agent = data.get('agent', 'main')
            content = data.get('content', '')
            
            memory_path = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / agent / "evolution" / "LEARNINGS.md"
            memory_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(memory_path, 'a', encoding='utf-8') as f:
                f.write(f"\n## {data.get('date', '')}: {data.get('title', '新记录')}\n{content}\n")
            
            self.send_json({'success': True})
        
        else:
            self.send_error(404)
    
    def send_json(self, data):
        """统一 JSON 响应并附带基础 CORS 头。"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        """记录标准访问日志。"""
        LOGGER.info(format % args)

if __name__ == "__main__":
    port = PORT_JOYMATE
    LOGGER.info("JoyMate API started: http://localhost:%s", port)
    HTTPServer(("0.0.0.0", port), JoyMateHandler).serve_forever()
