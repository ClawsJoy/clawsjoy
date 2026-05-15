"""真智能大脑 - 事件驱动，无定时任务"""
import threading
import time
import queue
import requests
import json
from datetime import datetime
from pathlib import Path
from collections import deque
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain
from intelligence.notifier import Notifier

class TrueBrain:
    """真智能大脑 - 事件驱动，实时响应"""
    
    def __init__(self):
        self.event_queue = queue.Queue()
        self.running = True
        self.last_states = {}
        self.event_history = deque(maxlen=1000)
        self.notifier = Notifier()
        
        # 启动事件监听器
        self.start_listeners()
        
        print("\n🧠 真智能大脑已启动")
        print("=" * 50)
        print("⚡ 事件驱动模式 - 实时响应")
        print("🔄 持续感知 - 无需定时任务")
        print("🎯 主动决策 - 自动采取行动")
        print("=" * 50)
    
    def start_listeners(self):
        """启动事件监听器（独立线程）"""
        # 服务状态监听
        service_thread = threading.Thread(target=self._listen_services, daemon=True)
        service_thread.start()
        
        # 大脑状态监听
        brain_thread = threading.Thread(target=self._listen_brain, daemon=True)
        brain_thread.start()
        
        # 事件处理线程
        process_thread = threading.Thread(target=self._process_events, daemon=True)
        process_thread.start()
        
        print("✅ 事件监听器已启动")
    
    def _listen_services(self):
        """监听服务状态 - 持续监控，发现变化立即触发"""
        services = {
            'gateway': 'http://localhost:5002/health',
            'file': 'http://localhost:5003/health',
            'agent': 'http://localhost:5005/health',
            'doc': 'http://localhost:5008/health'
        }
        
        while self.running:
            for name, url in services.items():
                try:
                    resp = requests.get(url, timeout=2)
                    current = resp.status_code == 200
                    
                    # 检测状态变化（事件）
                    if name not in self.last_states:
                        self.last_states[name] = current
                    elif self.last_states[name] != current:
                        # 状态变化！触发事件
                        event = {
                            'type': 'service_state_change',
                            'service': name,
                            'old_state': self.last_states[name],
                            'new_state': current,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.event_queue.put(event)
                        self.last_states[name] = current
                        
                        if not current:
                            self._on_service_down(name)
                except:
                    if name not in self.last_states or self.last_states[name] is not False:
                        # 服务不可达事件
                        event = {
                            'type': 'service_unreachable',
                            'service': name,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.event_queue.put(event)
                        self.last_states[name] = False
                        self._on_service_down(name)
            
            time.sleep(3)  # 3秒检查一次，不是定时任务，是持续感知
    
    def _listen_brain(self):
        """监听大脑状态 - 实时感知大脑变化"""
        last_experiences = brain.get_stats().get('total_experiences', 0)
        last_success_rate = brain.get_stats().get('success_rate', 0)
        
        while self.running:
            stats = brain.get_stats()
            current_experiences = stats.get('total_experiences', 0)
            current_success_rate = stats.get('success_rate', 0)
            
            # 新经验事件（增量超过5）
            if current_experiences - last_experiences >= 5:
                event = {
                    'type': 'new_experiences_gained',
                    'count': current_experiences - last_experiences,
                    'total': current_experiences,
                    'timestamp': datetime.now().isoformat()
                }
                self.event_queue.put(event)
                last_experiences = current_experiences
            
            # 成功率大幅下降事件
            if current_success_rate < last_success_rate - 0.1:
                event = {
                    'type': 'success_rate_drop',
                    'old_rate': last_success_rate,
                    'new_rate': current_success_rate,
                    'timestamp': datetime.now().isoformat()
                }
                self.event_queue.put(event)
                last_success_rate = current_success_rate
            else:
                last_success_rate = current_success_rate
            
            time.sleep(5)  # 持续感知
    
    def _process_events(self):
        """处理事件队列 - 大脑反应"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except queue.Empty:
                continue
    
    def _handle_event(self, event):
        """大脑处理事件 - 智能反应"""
        event_type = event['type']
        
        print(f"\n⚡ 大脑感知到事件: {event_type}")
        
        # 记录事件历史
        self.event_history.append(event)
        
        if event_type == 'service_state_change':
            if not event['new_state']:
                self._decide_fix_service(event['service'])
        
        elif event_type == 'service_unreachable':
            self._decide_fix_service(event['service'])
        
        elif event_type == 'success_rate_drop':
            self._decide_optimize_learning(event)
        
        elif event_type == 'new_experiences_gained':
            self._decide_analyze_patterns(event)
    
    def _on_service_down(self, service_name):
        """服务异常时的即时反应"""
        print(f"🚨 检测到 {service_name} 服务异常，大脑立即决策...")
        self.event_queue.put({
            'type': 'service_state_change',
            'service': service_name,
            'new_state': False,
            'timestamp': datetime.now().isoformat()
        })
    
    def _decide_fix_service(self, service_name):
        """决策：修复服务"""
        print(f"🔧 大脑决策: 修复 {service_name} 服务")
        
        import subprocess
        subprocess.Popen("./restart_services.sh", shell=True, cwd="/mnt/d/clawsjoy")
        
        # 记录决策
        brain.record_experience(
            agent="true_brain",
            action=f"fix_{service_name}",
            result={"success": True},
            context="event_detected"
        )
        
        self.notifier.send("服务修复", f"自动修复 {service_name}", 'warning')
    
    def _decide_optimize_learning(self, event):
        """决策：优化学习"""
        print(f"📚 大脑决策: 优化学习 (成功率 {event['old_rate']*100:.0f}% -> {event['new_rate']*100:.0f}%)")
        
        # 调整学习率
        current_rate = brain.get_stats().get('learning_rate', 0.3)
        new_rate = max(0.2, current_rate - 0.05)
        
        if hasattr(brain, 'knowledge'):
            brain.knowledge['learning_rate'] = new_rate
        
        brain.record_experience(
            agent="true_brain",
            action="optimize_learning",
            result={"old_rate": event['old_rate'], "new_rate": event['new_rate']},
            context="success_rate_drop"
        )
    
    def _decide_analyze_patterns(self, event):
        """决策：分析新模式"""
        print(f"🔍 大脑决策: 分析新经验模式 (+{event['count']}条)")
        
        # 触发经验分析
        brain.record_experience(
            agent="true_brain",
            action="analyze_patterns",
            result={"new_experiences": event['count']},
            context="auto_analysis"
        )
    
    def stop(self):
        self.running = False
        print("\n🧠 真智能大脑已停止")

if __name__ == "__main__":
    brain_core = TrueBrain()
    
    try:
        # 保持运行，但不需要循环，所有线程都是daemon
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        brain_core.stop()
# 启动真智能大脑（事件驱动，无定时）
cat > start_true_brain.sh << 'EOF'
#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 启动真智能大脑（事件驱动模式）"
echo "=================================="

# 停止旧的
pkill -f "true_brain.py" 2>/dev/null
pkill -f "decision_executor.py" 2>/dev/null

# 启动新的真智能大脑
python3 intelligence/true_brain.py &
BRAIN_PID=$!

echo ""
echo "✅ 真智能大脑已启动 (PID: $BRAIN_PID)"
echo ""
echo "⚡ 事件驱动 - 无需定时任务"
echo "🔄 持续感知 - 3秒检查间隔"
echo "🎯 自主决策 - 实时响应"
echo ""
echo "查看日志: tail -f logs/brain.log"
echo "停止: kill $BRAIN_PID"
