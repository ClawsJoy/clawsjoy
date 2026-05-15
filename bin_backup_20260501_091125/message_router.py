#!/usr/bin/env python3
"""
ClawsJoy 消息路由基础版
根据规则将请求分发到不同执行引擎
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入适配器
from executor_adapter import ExecutorRouter, OpenClawAdapter, ClaudeCodeAdapter

class MessageRouter:
    """消息路由器"""
    
    def __init__(self):
        self.router = ExecutorRouter()
        self.rules = self._load_rules()
        self.stats = {"total": 0, "by_engine": {}}
    
    def _load_rules(self) -> List[Dict]:
        """加载路由规则"""
        rules_file = Path("/mnt/d/clawsjoy/config/rules.json")
        if rules_file.exists():
            return json.loads(rules_file.read_text())
        
        # 默认规则
        default_rules = [
            {
                "name": "编程任务",
                "pattern": r"(写|生成|创建|修改|重构|优化|调试).*(代码|函数|类|脚本|程序)",
                "engine": "claude_code",
                "priority": 10
            },
            {
                "name": "代码审查",
                "pattern": r"(审查|检查|review).*(代码|逻辑|错误|bug)",
                "engine": "claude_code",
                "priority": 10
            },
            {
                "name": "宣传片制作",
                "pattern": r"(制作|创建).*(宣传片|视频)",
                "engine": "openclaw",
                "priority": 8
            },
            {
                "name": "图片采集",
                "pattern": r"(采集|下载|获取).*(图片|照片|素材)",
                "engine": "openclaw",
                "priority": 8
            },
            {
                "name": "对话聊天",
                "pattern": r"^(你好|嗨|hello|hi|在吗|聊聊|对话)",
                "engine": "openclaw",
                "priority": 5
            },
            {
                "name": "通用任务",
                "pattern": r".*",
                "engine": "openclaw",
                "priority": 0
            }
        ]
        return default_rules
    
    def _save_rules(self):
        """保存规则"""
        rules_file = Path("/mnt/d/clawsjoy/config/rules.json")
        rules_file.parent.mkdir(parents=True, exist_ok=True)
        rules_file.write_text(json.dumps(self.rules, indent=2, ensure_ascii=False))
    
    def match_rule(self, message: str) -> Optional[Dict]:
        """匹配规则"""
        matched = []
        for rule in self.rules:
            if re.search(rule["pattern"], message, re.IGNORECASE):
                matched.append(rule)
        
        if not matched:
            return None
        
        # 按优先级排序，返回最高优先级的
        matched.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return matched[0]
    
    def route(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """路由消息到合适的引擎"""
        self.stats["total"] += 1
        
        # 匹配规则
        rule = self.match_rule(message)
        
        if rule:
            engine_name = rule["engine"]
            print(f"📋 匹配规则: {rule['name']} -> {engine_name}")
        else:
            engine_name = "openclaw"
            print(f"📋 无匹配规则，使用默认引擎: {engine_name}")
        
        # 统计
        self.stats["by_engine"][engine_name] = self.stats["by_engine"].get(engine_name, 0) + 1
        
        # 构建任务
        task = {
            "task_type": self._detect_task_type(message),
            "prompt": message,
            "context": context or {},
            "routed_at": datetime.now().isoformat(),
            "matched_rule": rule["name"] if rule else None
        }
        
        # 执行
        if engine_name == "claude_code":
            adapter = ClaudeCodeAdapter()
        else:
            adapter = OpenClawAdapter()
        
        result = adapter.execute(task)
        result["routed_by"] = "message_router"
        result["matched_rule"] = rule["name"] if rule else "default"
        
        return result
    
    def _detect_task_type(self, message: str) -> str:
        """检测任务类型"""
        if re.search(r"(写|生成|创建).*(代码|函数)", message):
            return "code_generation"
        elif re.search(r"(审查|检查).*(代码)", message):
            return "code_review"
        elif re.search(r"(制作|创建).*(宣传片|视频)", message):
            return "promo"
        elif re.search(r"(采集|下载).*(图片)", message):
            return "spider"
        else:
            return "chat"
    
    def add_rule(self, name: str, pattern: str, engine: str, priority: int = 5):
        """添加路由规则"""
        self.rules.append({
            "name": name,
            "pattern": pattern,
            "engine": engine,
            "priority": priority
        })
        self._save_rules()
        print(f"✅ 规则已添加: {name}")
    
    def list_rules(self) -> List[Dict]:
        """列出所有规则"""
        return self.rules
    
    def get_stats(self) -> Dict:
        """获取路由统计"""
        return self.stats
    
    def add_tenant_rule(self, tenant_id: str, pattern: str, engine: str):
        """为特定租户添加规则"""
        tenant_rules_file = Path(f"/mnt/d/clawsjoy/tenants/tenant_{tenant_id}/rules.json")
        if tenant_rules_file.exists():
            rules = json.loads(tenant_rules_file.read_text())
        else:
            rules = []
        
        rules.append({
            "name": f"tenant_{tenant_id}_rule",
            "pattern": pattern,
            "engine": engine,
            "priority": 15,
            "tenant_id": tenant_id
        })
        tenant_rules_file.write_text(json.dumps(rules, indent=2))
        print(f"✅ 租户 {tenant_id} 规则已添加")


# HTTP API 服务
from http.server import HTTPServer, BaseHTTPRequestHandler

router = MessageRouter()

class RouterHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/router/route':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            message = data.get('message', '')
            context = data.get('context', {})
            
            result = router.route(message, context)
            self.send_json(result)
        
        elif self.path == '/api/router/add_rule':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            router.add_rule(
                name=data.get('name', '新规则'),
                pattern=data.get('pattern', '.*'),
                engine=data.get('engine', 'openclaw'),
                priority=data.get('priority', 5)
            )
            self.send_json({"success": True})
        
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/api/router/rules':
            self.send_json({"rules": router.list_rules()})
        elif self.path == '/api/router/stats':
            self.send_json({"stats": router.get_stats()})
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == "route":
            message = " ".join(sys.argv[2:])
            result = router.route(message)
            print(f"引擎: {result.get('engine')}")
            print(f"输出: {result.get('output', '')[:200]}")
        elif sys.argv[1] == "rules":
            for r in router.list_rules():
                print(f"{r['name']}: {r['pattern']} -> {r['engine']}")
        elif sys.argv[1] == "stats":
            print(json.dumps(router.get_stats(), indent=2))
    else:
        # 启动 HTTP 服务
        port = 8089
        print(f"🚦 消息路由器 API: http://localhost:{port}")
        print(f"   POST /api/router/route - 路由消息")
        print(f"   GET  /api/router/rules - 查看规则")
        print(f"   POST /api/router/add_rule - 添加规则")
        HTTPServer(("0.0.0.0", port), RouterHandler).serve_forever()
