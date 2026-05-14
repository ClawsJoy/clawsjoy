from lib.unified_config import config
#!/usr/bin/env python3
"""
真智能核心 v2 - 事件驱动、LLM决策、强化学习
"""

import asyncio
import threading
import time
import json
import subprocess
import requests
from datetime import datetime
from collections import deque
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class TrueIntelligenceV2:
    """真智能核心"""
    
    def __init__(self):
        # 实时事件队列
        self.event_queue = deque(maxlen=1000)
        self.running = True
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # 经验池
        self.experience_pool = []
        self.decision_cache = {}
        
        # 启动核心线程
        self._start_threads()
        
        print("🧠 真智能核心 v2 已启动")
        print("   - 事件驱动 (实时响应)")
        print("   - LLM 决策 (智能推理)")
        print("   - 强化学习 (持续优化)")
    
    def _start_threads(self):
        """启动核心线程"""
        threads = [
            threading.Thread(target=self._event_loop, daemon=True),
            threading.Thread(target=self._decision_loop, daemon=True),
            threading.Thread(target=self._learning_loop, daemon=True),
        ]
        for t in threads:
            t.start()
    
    def emit_event(self, event_type, data):
        """发送事件（实时）"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
            "id": len(self.event_queue)
        }
        self.event_queue.append(event)
        print(f"⚡ 事件触发: {event_type}")
    
    def _event_loop(self):
        """事件循环 - 实时处理"""
        while self.running:
            if self.event_queue:
                event = self.event_queue.popleft()
                self._handle_event(event)
            else:
                time.sleep(0.1)  # 100ms 轮询，接近实时
    
    def _handle_event(self, event):
        """处理事件"""
        event_type = event["type"]
        
        # 预定义事件处理器
        handlers = {
            "api_down": self._handle_api_down,
            "ollama_slow": self._handle_ollama_slow,
            "disk_full": self._handle_disk_full,
            "error_rate_high": self._handle_error_high,
            "session_peak": self._handle_session_peak,
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(event["data"])
        else:
            # 未知事件，LLM 决策
            self._llm_decide(event)
    
    def _handle_api_down(self, data):
        """API 宕机处理"""
        print(f"🚨 API 宕机: {data}")
        # 尝试重启
        subprocess.Popen("cd /mnt/d/clawsjoy && python3 agent_gateway_web.py &", shell=True)
        brain.record_experience("intelligence", "api_down_handled", {"success": True})
    
    def _handle_ollama_slow(self, data):
        """Ollama 慢处理"""
        print(f"🐢 Ollama 响应慢: {data}")
        # 切换小模型
        subprocess.run("ollama pull llama3.2:1b", shell=True)
    
    def _handle_disk_full(self, data):
        """磁盘满处理"""
        print(f"💾 磁盘空间不足: {data}")
        subprocess.run("find /mnt/d/clawsjoy/logs -name '*.log' -mtime +3 -delete", shell=True)
    
    def _handle_error_high(self, data):
        """错误率过高"""
        print(f"⚠️ 错误率过高: {data}")
        # 触发学习
        self._trigger_learning()
    
    def _handle_session_peak(self, data):
        """会话高峰"""
        print(f"📈 会话高峰: {data}")
        # 扩容或限流
        pass
    
    def _llm_decide(self, event):
        """LLM 决策未知事件"""
        prompt = f"""事件类型: {event['type']}
事件数据: {event['data']}
历史经验: {brain.get_stats()}

请决策如何处理，输出 JSON:
{{
    "action": "要执行的动作",
    "command": "具体命令",
    "priority": "high/medium/low"
}}"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": config.LLM["default_model"],
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            decision = resp.json().get('response', '')
            start = decision.find('{')
            end = decision.rfind('}') + 1
            if start != -1:
                action = json.loads(decision[start:end])
                self._execute_decision(action)
        except Exception as e:
            print(f"LLM 决策失败: {e}")
    
    def _execute_decision(self, action):
        """执行决策"""
        cmd = action.get('command')
        if cmd:
            print(f"🔧 执行: {cmd[:80]}")
            subprocess.Popen(cmd, shell=True)
            brain.record_experience(
                agent="intelligence",
                action=f"decision_{action.get('action')}",
                result={"success": True}
            )
    
    def _decision_loop(self):
        """决策循环 - 主动决策"""
        while self.running:
            try:
                # 1. 评估系统状态
                stats = brain.get_stats()
                success_rate = stats.get('success_rate', 0.9)
                
                # 2. 决策：是否需要干预？
                if success_rate < 0.7:
                    self.emit_event("error_rate_high", {"rate": success_rate})
                
                # 3. 决策：是否需要学习？
                if stats.get('total_experiences', 0) < 50:
                    self._trigger_learning()
                
                # 4. 决策：是否需要探索？
                if len(brain.knowledge.get('knowledge_graph', [])) < 20:
                    self._trigger_exploration()
                
                time.sleep(30)  # 30秒决策周期
                
            except Exception as e:
                print(f"决策错误: {e}")
                time.sleep(10)
    
    def _trigger_learning(self):
        """触发学习"""
        print("📚 触发学习...")
        try:
            from agents.core.active_explorer import active_explorer
            active_explorer.explore(rounds=1)
        except:
            pass
    
    def _trigger_exploration(self):
        """触发探索"""
        print("🔍 触发探索...")
        # 探索新技能
        from skills.skill_interface import skill_registry
        skills = skill_registry.get_skill_names()
        if skills:
            import random
            test_skill = random.choice(skills[:10])
            print(f"🧪 探索技能: {test_skill}")
    
    def _learning_loop(self):
        """学习循环 - 强化学习"""
        while self.running:
            try:
                # 分析近期待改进点
                recent_exps = brain.knowledge.get('experiences', [])[-20:]
                failures = [e for e in recent_exps if not e.get('result', {}).get('success')]
                
                if len(failures) > 5:
                    print(f"📊 发现 {len(failures)} 个失败案例，触发反思")
                    self._trigger_reflection(failures)
                
                time.sleep(60)  # 每分钟学习一次
                
            except Exception as e:
                print(f"学习错误: {e}")
                time.sleep(30)
    
    def _trigger_reflection(self, failures):
        """触发反思"""
        prompt = f"""分析这些失败案例，找出共同模式:
{json.dumps(failures, indent=2)[:500]}

输出改进建议。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": config.LLM["default_model"],
                "prompt": prompt,
                "stream": False
            }, timeout=60)
            suggestion = resp.json().get('response', '')
            print(f"💡 反思建议: {suggestion[:200]}")
            
            brain.record_experience(
                agent="intelligence",
                action="reflection",
                result={"success": True, "suggestion": suggestion[:100]}
            )
        except:
            pass
    
    def monitor(self):
        """持续监控 - 主动检测异常"""
        last_api_status = True
        last_disk = 0
        
        while self.running:
            try:
                # 检测 API
                api_ok = self._check_api()
                if not api_ok and last_api_status:
                    self.emit_event("api_down", {"time": datetime.now().isoformat()})
                last_api_status = api_ok
                
                # 检测磁盘
                disk = self._get_disk_usage()
                if disk > 85 and last_disk <= 85:
                    self.emit_event("disk_full", {"usage": disk})
                last_disk = disk
                
                # 检测 Ollama 响应
                ollama_time = self._check_ollama_latency()
                if ollama_time > 5:
                    self.emit_event("ollama_slow", {"latency": ollama_time})
                
                time.sleep(10)  # 10秒监控周期
                
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(5)
    
    def _check_api(self):
        try:
            resp = requests.get("http://localhost:5002/api/health", timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def _get_disk_usage(self):
        result = subprocess.run("df -h / | tail -1 | awk '{print $5}'", 
                                shell=True, capture_output=True, text=True)
        disk = result.stdout.strip().replace('%', '')
        return int(disk) if disk.isdigit() else 0
    
    def _check_ollama_latency(self):
        try:
            start = time.time()
            requests.get("http://localhost:11434/api/tags", timeout=5)
            return time.time() - start
        except:
            return 999
    
    def start(self):
        """启动所有服务"""
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor, daemon=True)
        monitor_thread.start()
        
        print("✅ 真智能核心运行中")
        print("   监控: 10秒/次 | 决策: 30秒/次 | 学习: 60秒/次")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n智能核心已停止")

if __name__ == '__main__':
    intelligence = TrueIntelligenceV2()
    intelligence.start()
