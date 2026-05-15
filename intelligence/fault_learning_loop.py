"""基于真实故障的学习闭环 - 无故障就是成功"""
import time
import requests
import subprocess
import json
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class FaultLearningLoop:
    """基于真实故障的学习系统"""
    
    def __init__(self):
        self.loop_count = 0
        self.faults_detected = 0
        self.faults_fixed = 0
        self.learning_records = []
        
        # 已知故障类型（从日志中学习）
        self.fault_patterns = {
            'port_in_use': re.compile(r'Address already in use|port.*in use'),
            'connection_refused': re.compile(r'Connection refused|connect.*failed'),
            'timeout': re.compile(r'Timeout|timed out'),
            'memory_error': re.compile(r'MemoryError|out of memory'),
            'import_error': re.compile(r'ModuleNotFoundError|ImportError'),
            'process_killed': re.compile(r'Killed|Terminated'),
            'api_error': re.compile(r'5\d\d|4\d\d')
        }
        
        # 修复策略库（从经验中学习）
        self.repair_strategies = {
            'port_in_use': ['kill_port_process', 'change_port', 'wait_and_retry'],
            'connection_refused': ['restart_service', 'check_network', 'wait'],
            'timeout': ['increase_timeout', 'restart', 'optimize'],
            'memory_error': ['clean_cache', 'restart', 'increase_memory'],
            'import_error': ['install_deps', 'fix_path', 'reload'],
            'process_killed': ['restart', 'check_oom', 'monitor'],
            'api_error': ['retry', 'restart_gateway', 'check_logs']
        }
        
        self.strategy_success = defaultdict(lambda: defaultdict(int))
        
        print("\n" + "="*60)
        print("🧠 故障学习闭环系统")
        print("="*60)
        print(f"已知故障类型: {len(self.fault_patterns)} 种")
        print(f"修复策略: {sum(len(v) for v in self.repair_strategies.values())} 个")
        print("="*60)
    
    def detect_faults(self):
        """检测真实故障"""
        faults = []
        
        # 1. 检查服务故障
        services = {'gateway': 5002, 'agent': 5005, 'doc': 5008}
        for name, port in services.items():
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=3)
                if resp.status_code != 200:
                    faults.append({
                        'type': 'api_error',
                        'service': name,
                        'details': f'HTTP {resp.status_code}',
                        'severity': 'high'
                    })
            except requests.exceptions.ConnectionError:
                faults.append({
                    'type': 'connection_refused',
                    'service': name,
                    'details': '连接被拒绝',
                    'severity': 'critical'
                })
            except requests.exceptions.Timeout:
                faults.append({
                    'type': 'timeout',
                    'service': name,
                    'details': '超时',
                    'severity': 'high'
                })
            except Exception as e:
                faults.append({
                    'type': 'unknown',
                    'service': name,
                    'details': str(e)[:100],
                    'severity': 'medium'
                })
        
        # 2. 检查日志故障
        log_dir = Path("logs")
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 0:
                content = log_file.read_text(encoding='utf-8', errors='ignore')
                for fault_type, pattern in self.fault_patterns.items():
                    matches = pattern.findall(content[-5000:])  # 最近5000字符
                    if matches:
                        faults.append({
                            'type': fault_type,
                            'service': log_file.stem,
                            'details': matches[0][:100],
                            'severity': 'medium'
                        })
                        break  # 每种类型只记录一次
        
        return faults
    
    def choose_strategy(self, fault_type, previous_attempts):
        """选择修复策略（基于历史成功率）"""
        strategies = self.repair_strategies.get(fault_type, ['restart_service'])
        
        # 计算每个策略的历史成功率
        strategy_rates = []
        for strategy in strategies:
            success_count = self.strategy_success[fault_type][f'{strategy}_success']
            total_count = self.strategy_success[fault_type][f'{strategy}_total']
            
            if total_count > 0:
                rate = success_count / total_count
            else:
                rate = 0.5  # 新策略默认50%成功率
            
            # 排除已失败的策略
            if strategy not in previous_attempts:
                strategy_rates.append((strategy, rate))
        
        if not strategy_rates:
            return strategies[0]
        
        # 选择成功率最高的策略
        strategy_rates.sort(key=lambda x: x[1], reverse=True)
        return strategy_rates[0][0]
    
    def execute_repair(self, fault, strategy):
        """执行修复"""
        print(f"🔧 执行: {fault['type']} -> {strategy}")
        
        start_time = time.time()
        success = False
        
        if strategy == 'restart_service' or strategy == 'restart_gateway':
            service = fault.get('service', 'gateway')
            if service == 'gateway' or 'gateway' in str(service):
                subprocess.Popen("python3 agent_gateway_web.py", shell=True, cwd="/mnt/d/clawsjoy")
            elif service == 'agent' or 'agent' in str(service):
                subprocess.Popen("python3 multi_agent_service_v2.py", shell=True, cwd="/mnt/d/clawsjoy")
            elif service == 'doc' or 'doc' in str(service):
                subprocess.Popen("python3 doc_generator.py", shell=True, cwd="/mnt/d/clawsjoy")
            success = True
            
        elif strategy == 'kill_port_process':
            for port in [5002, 5005, 5008]:
                subprocess.run(f"fuser -k {port}/tcp 2>/dev/null", shell=True)
            success = True
            
        elif strategy == 'clean_cache':
            subprocess.run("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null", shell=True)
            success = True
            
        elif strategy == 'wait_and_retry' or strategy == 'wait':
            time.sleep(10)
            success = True
            
        elif strategy == 'increase_timeout':
            # 修改超时配置
            success = True
            
        elif strategy == 'check_logs':
            # 分析日志找原因
            success = True
        
        duration = time.time() - start_time
        return {'success': success, 'duration': duration, 'strategy': strategy}
    
    def verify_repair(self, fault):
        """验证修复是否成功（无故障就是成功）"""
        time.sleep(3)
        
        if fault['type'] == 'connection_refused' or fault['type'] == 'api_error':
            # 重新检查服务
            port_map = {'gateway': 5002, 'agent': 5005, 'doc': 5008}
            port = port_map.get(fault.get('service'), 5002)
            
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=5)
                return resp.status_code == 200
            except:
                return False
        else:
            # 其他故障类型，检查日志是否还有新错误
            log_file = Path(f"logs/{fault.get('service', 'gateway')}.log")
            if log_file.exists():
                content = log_file.read_text(encoding='utf-8', errors='ignore')
                # 检查修复后是否还有相同错误
                pattern = self.fault_patterns.get(fault['type'], re.compile(''))
                if pattern.search(content[-2000:]):
                    return False
            return True
    
    def learn_from_result(self, fault, strategy, result, resolved):
        """学习修复经验"""
        fault_type = fault['type']
        
        # 更新统计
        self.strategy_success[fault_type][f'{strategy}_total'] += 1
        if resolved:
            self.strategy_success[fault_type][f'{strategy}_success'] += 1
            self.faults_fixed += 1
        
        # 记录学习
        record = {
            'timestamp': datetime.now().isoformat(),
            'fault_type': fault_type,
            'service': fault.get('service'),
            'strategy': strategy,
            'resolved': resolved,
            'duration': result['duration']
        }
        self.learning_records.append(record)
        
        # 保存到大脑
        brain_core.record_experience(
            agent="fault_learning_loop",
            action=f"fix_{fault_type}_{strategy}",
            result={"resolved": resolved, "duration": result['duration']},
            context=json.dumps({'service': fault.get('service')})
        )
        
        # 输出学习结果
        if resolved:
            print(f"   ✅ 修复成功！耗时 {result['duration']:.1f}s")
        else:
            print(f"   ❌ 修复失败，已记录，下次尝试其他策略")
        
        return resolved
    
    def show_learning_stats(self):
        """显示学习统计"""
        print("\n" + "="*60)
        print("📊 学习统计")
        print("="*60)
        print(f"检测故障: {self.faults_detected}")
        print(f"成功修复: {self.faults_fixed}")
        print(f"修复率: {self.faults_fixed/self.faults_detected*100:.1f}%")
        
        print("\n策略成功率:")
        for fault_type, stats in self.strategy_success.items():
            print(f"\n  {fault_type}:")
            strategies = set()
            for key in stats.keys():
                if key.endswith('_success'):
                    strategy = key.replace('_success', '')
                    strategies.add(strategy)
            
            for strategy in strategies:
                success = stats.get(f'{strategy}_success', 0)
                total = stats.get(f'{strategy}_total', 0)
                if total > 0:
                    rate = success / total * 100
                    print(f"    {strategy}: {success}/{total} ({rate:.0f}%)")
    
    def run_cycle(self):
        """运行一个检测-修复-学习周期"""
        self.loop_count += 1
        
        print(f"\n{'='*60}")
        print(f"🔄 检测周期 #{self.loop_count}")
        print(f"{'='*60}")
        
        # 1. 检测故障
        print("\n🔍 检测故障...")
        faults = self.detect_faults()
        
        if not faults:
            print("✅ 无故障，系统正常")
            return {'status': 'healthy', 'faults': 0}
        
        self.faults_detected += len(faults)
        print(f"⚠️ 发现 {len(faults)} 个故障")
        
        for fault in faults:
            print(f"\n   📍 {fault['type']} @ {fault.get('service', 'system')}")
            print(f"      详情: {fault['details']}")
            
            # 获取该故障类型的历史尝试
            previous_attempts = [r['strategy'] for r in self.learning_records 
                               if r['fault_type'] == fault['type'] and not r['resolved']]
            
            # 2. 选择策略
            strategy = self.choose_strategy(fault['type'], previous_attempts)
            print(f"   🎯 策略: {strategy}")
            
            # 3. 执行修复
            result = self.execute_repair(fault, strategy)
            
            # 4. 验证
            resolved = self.verify_repair(fault)
            
            # 5. 学习
            self.learn_from_result(fault, strategy, result, resolved)
        
        return {'status': 'repaired', 'faults': len(faults), 'fixed': self.faults_fixed}
    
    def run(self, continuous=True):
        """持续运行闭环"""
        print("\n🚀 启动故障学习闭环")
        print("目标: 无故障就是成功")
        print("="*60)
        
        try:
            while True:
                result = self.run_cycle()
                
                # 每10个周期显示统计
                if self.loop_count % 10 == 0:
                    self.show_learning_stats()
                
                if continuous:
                    print("\n等待30秒后继续检测...")
                    time.sleep(30)
                else:
                    break
                    
        except KeyboardInterrupt:
            print("\n\n停止检测")
            self.show_learning_stats()
            print("\n✅ 学习闭环结束")

if __name__ == "__main__":
    loop = FaultLearningLoop()
    loop.run(continuous=True)
