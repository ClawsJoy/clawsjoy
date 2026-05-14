from lib.unified_config import config
#!/usr/bin/env python3
"""
真智能增强版 - 轻量级，可训练，不依赖大模型
"""

import threading
import time
import json
import subprocess
import requests
from collections import deque
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class TrueIntelligenceLight:
    """真智能增强版 - 轻量可训练"""
    
    def __init__(self):
        self.event_queue = deque(maxlen=500)
        self.running = True
        self.stats = {"events": 0, "decisions": 0, "learnings": 0}
        
        # 事件处理器（可训练）
        self.handlers = self._load_handlers()
        
        self._start()
        print("🧠 真智能增强版已启动")
        print("   - 事件驱动 | 主动决策 | 持续学习")
    
    def _load_handlers(self):
        """加载事件处理器（可从大脑学习）"""
        # 从大脑获取已学习的模式
        learned = brain.knowledge.get('learned_patterns', {})
        
        default = {
            "api_down": {"action": "restart_api", "cmd": "cd /mnt/d/clawsjoy && python3 agent_gateway_web.py &"},
            "disk_full": {"action": "clean_logs", "cmd": "find /mnt/d/clawsjoy/logs -name '*.log' -mtime +3 -delete"},
            "ollama_slow": {"action": "switch_model", "cmd": "ollama pull llama3.2:1b"},
            "high_cpu": {"action": "kill_zombie", "cmd": "pkill -f defunct"},
        }
        
        # 合并已学习的模式
        for k, v in learned.items():
            default[k] = v
        
        return default
    
    def _save_handler(self, event_type, handler):
        """保存学到的事件处理方式"""
        learned = brain.knowledge.get('learned_patterns', {})
        learned[event_type] = handler
        brain.knowledge['learned_patterns'] = learned
        brain._save()
    
    def emit(self, event_type, data):
        """发送事件"""
        self.event_queue.append({
            "type": event_type,
            "data": data,
            "time": time.time()
        })
        self.stats["events"] += 1
        print(f"⚡ 事件: {event_type}")
    
    def _process_events(self):
        """处理事件循环"""
        while self.running:
            if self.event_queue:
                event = self.event_queue.popleft()
                self._handle_event(event)
            else:
                time.sleep(0.1)
    
    def _handle_event(self, event):
        """处理事件"""
        event_type = event["type"]
        
        if event_type in self.handlers:
            handler = self.handlers[event_type]
            print(f"🔧 执行: {handler['action']}")
            subprocess.Popen(handler['cmd'], shell=True)
            self.stats["decisions"] += 1
            
            # 记录成功经验
            brain.record_experience(
                agent="intelligence",
                action=f"handle_{event_type}",
                result={"success": True},
                context=handler['cmd']
            )
        else:
            # 未知事件，触发学习
            self._learn_event(event)
    
    def _learn_event(self, event):
        """学习新事件"""
        print(f"📚 学习新事件: {event['type']}")
        
        # 尝试用 LLM 推理（可选，可关闭）
        try:
            prompt = f"事件: {event['type']}\n数据: {event['data']}\n输出修复命令"
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": config.LLM["default_model"], "prompt": prompt, "stream": False},
                timeout=30)
            cmd = resp.json().get('response', '').strip()
            
            if cmd and len(cmd) < 200:
                self.handlers[event['type']] = {
                    "action": f"learned_{event['type']}",
                    "cmd": cmd
                }
                self._save_handler(event['type'], self.handlers[event['type']])
                print(f"   ✅ 已学习: {cmd[:50]}...")
        except:
            pass
        
        self.stats["learnings"] += 1
    
    def _monitor(self):
        """监控循环 - 主动发现事件"""
        last_api = True
        last_disk = 0
        
        while self.running:
            try:
                # 检测 API
                api_ok = self._check_api()
                if not api_ok and last_api:
                    self.emit("api_down", {"time": time.time()})
                last_api = api_ok
                
                # 检测磁盘
                disk = self._get_disk()
                if disk > 85 and last_disk <= 85:
                    self.emit("disk_full", {"usage": disk})
                last_disk = disk
                
                # 检测 CPU
                cpu = self._get_cpu()
                if cpu > 80:
                    self.emit("high_cpu", {"usage": cpu})
                
                time.sleep(15)
                
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(5)
    
    def _check_api(self):
        try:
            resp = requests.get("http://localhost:5002/api/health", timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def _get_disk(self):
        result = subprocess.run("df -h / | tail -1 | awk '{print $5}'", 
                                shell=True, capture_output=True, text=True)
        disk = result.stdout.strip().replace('%', '')
        return int(disk) if disk.isdigit() else 0
    
    def _get_cpu(self):
        result = subprocess.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", 
                                shell=True, capture_output=True, text=True)
        cpu = result.stdout.strip()
        return float(cpu) if cpu else 0
    
    def _decision(self):
        """决策循环 - 自主决定做什么"""
        while self.running:
            try:
                stats = brain.get_stats()
                
                # 决策：是否需要学习
                if stats['total_experiences'] < 30:
                    print("📚 决策: 需要更多经验")
                    self._trigger_learning()
                
                # 决策：是否需要优化
                if stats['success_rate'] < 0.7:
                    print("🎯 决策: 需要优化策略")
                    self._trigger_optimization()
                
                time.sleep(60)
                
            except Exception as e:
                print(f"决策错误: {e}")
                time.sleep(30)
    
    def _trigger_learning(self):
        """触发学习"""
        from skills.skill_interface import skill_registry
        skills = skill_registry.get_skill_names()
        if skills:
            import random
            test_skill = random.choice(skills[:10])
            print(f"🧪 学习新技能: {test_skill}")
    
    def _trigger_optimization(self):
        """触发优化"""
        subprocess.run("find /mnt/d/clawsjoy/logs -name '*.log' -mtime +7 -delete", shell=True)
        print("⚡ 执行优化: 清理旧日志")
    
    def _stats_report(self):
        """统计报告循环"""
        while self.running:
            time.sleep(300)  # 5分钟
            print(f"\n📊 智能核心统计: {self.stats}")
    
    def _start(self):
        """启动所有线程"""
        threads = [
            threading.Thread(target=self._process_events, daemon=True),
            threading.Thread(target=self._monitor, daemon=True),
            threading.Thread(target=self._decision, daemon=True),
            threading.Thread(target=self._stats_report, daemon=True),
        ]
        for t in threads:
            t.start()
    
    def run(self):
        """运行主循环"""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n智能核心已停止")

if __name__ == '__main__':
    intelligence = TrueIntelligenceLight()
    intelligence.run()
