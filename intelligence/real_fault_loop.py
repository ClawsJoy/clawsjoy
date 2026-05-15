"""基于真实故障的学习闭环 - 无mock，只有真实故障"""
import time
import requests
import subprocess
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class RealFaultLoop:
    """真实故障学习闭环"""
    
    def __init__(self):
        self.loop_count = 0
        self.faults_log = []
        self.repair_log = []
        
        # 从大脑加载历史学习
        self.load_learning()
        
        print("\n" + "="*60)
        print("🔴 真实故障学习闭环")
        print("="*60)
        print("监听真实故障 → 执行修复 → 验证 → 学习")
        print("="*60)
    
    def load_learning(self):
        """从大脑加载学习经验"""
        experiences = brain_core.knowledge.get('experiences', [])
        self.learned_strategies = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for exp in experiences:
            action = exp.get('action', '')
            if 'fix_' in action:
                fault_type = action.replace('fix_', '')
                success = exp.get('result', {}).get('success', False)
                self.learned_strategies[fault_type]['total'] += 1
                if success:
                    self.learned_strategies[fault_type]['success'] += 1
        
        print(f"📚 已加载 {len(self.learned_strategies)} 类故障经验")
    
    def detect_real_faults(self):
        """检测真实故障"""
        faults = []
        
        # 1. 检测服务故障
        services = {
            'gateway': {'port': 5002, 'cmd': 'python3 agent_gateway_web.py'},
            'agent': {'port': 5005, 'cmd': 'python3 multi_agent_service_v2.py'},
            'doc': {'port': 5008, 'cmd': 'python3 doc_generator.py'}
        }
        
        for name, config in services.items():
            try:
                resp = requests.get(f"http://localhost:{config['port']}/health", timeout=3)
                if resp.status_code != 200:
                    faults.append({
                        'type': 'service_error',
                        'name': name,
                        'details': f'HTTP {resp.status_code}',
                        'cmd': config['cmd']
                    })
                    print(f"  ❌ {name}: HTTP {resp.status_code}")
            except requests.exceptions.ConnectionError:
                faults.append({
                    'type': 'service_down',
                    'name': name,
                    'details': '连接失败',
                    'cmd': config['cmd']
                })
                print(f"  ❌ {name}: 服务停止")
            except Exception as e:
                faults.append({
                    'type': 'unknown',
                    'name': name,
                    'details': str(e)[:50],
                    'cmd': config['cmd']
                })
                print(f"  ❌ {name}: {str(e)[:30]}")
        
        # 2. 检测日志故障
        log_dir = Path("logs")
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 0:
                content = log_file.read_text(encoding='utf-8', errors='ignore')[-5000:]
                
                if 'Killed' in content or 'Terminated' in content:
                    faults.append({
                        'type': 'process_killed',
                        'name': log_file.stem,
                        'details': '进程被杀',
                        'cmd': f'python3 {log_file.stem}.py'
                    })
                    print(f"  💀 {log_file.stem}: 进程被杀")
                
                if 'MemoryError' in content or 'out of memory' in content:
                    faults.append({
                        'type': 'memory_error',
                        'name': log_file.stem,
                        'details': '内存不足',
                        'cmd': f'python3 {log_file.stem}.py'
                    })
                    print(f"  💾 {log_file.stem}: 内存错误")
        
        return faults
    
    def decide_strategy(self, fault):
        """决策修复策略（基于学习经验）"""
        fault_key = f"{fault['type']}_{fault['name']}"
        
        # 从学习经验中找最佳策略
        stats = self.learned_strategies.get(fault_key, {'success': 0, 'total': 0})
        
        if stats['total'] == 0:
            # 无经验，使用默认策略
            strategy = 'restart'
            confidence = 0.5
        else:
            success_rate = stats['success'] / stats['total']
            strategy = 'restart'  # 目前只有restart策略
            confidence = success_rate
        
        return {
            'strategy': strategy,
            'confidence': confidence,
            'reason': f'历史成功率 {stats["success"]}/{stats["total"]}' if stats['total'] > 0 else '首次故障'
        }
    
    def execute_repair(self, fault, strategy):
        """执行修复"""
        print(f"  🔧 执行: {strategy}")
        
        start = time.time()
        
        if strategy == 'restart':
            subprocess.Popen(fault['cmd'], shell=True, cwd="/mnt/d/clawsjoy")
            time.sleep(3)
        
        duration = time.time() - start
        return {'success': True, 'duration': duration}
    
    def verify_repair(self, fault):
        """验证修复"""
        time.sleep(5)
        
        # 检查服务是否恢复
        port_map = {'gateway': 5002, 'agent': 5005, 'doc': 5008}
        port = port_map.get(fault['name'])
        
        if port:
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=5)
                return resp.status_code == 200
            except:
                return False
        
        return True
    
    def learn_from_result(self, fault, strategy, result, resolved):
        """学习修复结果"""
        fault_key = f"{fault['type']}_{fault['name']}"
        
        # 更新学习统计
        self.learned_strategies[fault_key]['total'] += 1
        if resolved:
            self.learned_strategies[fault_key]['success'] += 1
        
        # 记录到大脑
        brain_core.record_experience(
            agent="real_fault_loop",
            action=f"fix_{fault_key}",
            result={"success": resolved, "duration": result['duration']},
            context=f"strategy_{strategy}"
        )
        
        # 记录到本地
        self.repair_log.append({
            'timestamp': datetime.now().isoformat(),
            'fault': fault,
            'resolved': resolved,
            'duration': result['duration']
        })
        
        status = "✅ 修复成功" if resolved else "❌ 修复失败"
        print(f"  {status} ({result['duration']:.1f}s)")
        
        return resolved
    
    def run_cycle(self):
        """运行一个检测-修复周期"""
        self.loop_count += 1
        
        print(f"\n{'='*50}")
        print(f"🔄 检测周期 #{self.loop_count}")
        print(f"{'='*50}")
        
        # 1. 检测故障
        print("🔍 检测真实故障...")
        faults = self.detect_real_faults()
        
        if not faults:
            print("✅ 无故障")
            return
        
        print(f"\n⚠️ 发现 {len(faults)} 个真实故障")
        
        # 2. 处理每个故障
        for fault in faults:
            print(f"\n📍 {fault['type']} @ {fault['name']}")
            print(f"   详情: {fault['details']}")
            
            # 决策
            decision = self.decide_strategy(fault)
            print(f"   🎯 决策: {decision['strategy']} (置信度 {decision['confidence']:.0%})")
            print(f"   💭 理由: {decision['reason']}")
            
            # 执行
            result = self.execute_repair(fault, decision['strategy'])
            
            # 验证
            resolved = self.verify_repair(fault)
            
            # 学习
            self.learn_from_result(fault, decision['strategy'], result, resolved)
    
    def show_stats(self):
        """显示统计"""
        print("\n" + "="*50)
        print("📊 学习统计")
        print("="*50)
        print(f"检测周期: {self.loop_count}")
        print(f"修复记录: {len(self.repair_log)}")
        
        # 显示各故障类型的成功率
        if self.learned_strategies:
            print("\n故障类型成功率:")
            for fault, stats in list(self.learned_strategies.items())[:5]:
                rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
                print(f"  {fault}: {stats['success']}/{stats['total']} ({rate:.0%})")
    
    def run(self):
        """持续运行"""
        try:
            while True:
                self.run_cycle()
                self.show_stats()
                print("\n⏳ 等待60秒...")
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n停止闭环")
            self.show_stats()

if __name__ == "__main__":
    loop = RealFaultLoop()
    loop.run()
