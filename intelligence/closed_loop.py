"""智能闭环系统 - 感知→决策→执行→验证→学习"""
import time
import requests
import subprocess
import json
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class IntelligentClosedLoop:
    """真正的智能闭环"""
    
    def __init__(self):
        self.loop_count = 0
        self.decisions = defaultdict(list)
        self.running = True
        self.learning_history = []
        
    def perceive(self):
        """感知模块 - 收集数据"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'resources': {}
        }
        
        # 感知服务
        for name, port in [('gateway',5002), ('agent',5005), ('doc',5008)]:
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=2)
                state['services'][name] = resp.status_code == 200
            except:
                state['services'][name] = False
        
        return state
    
    def decide(self, state):
        """决策模块 - 基于历史学习"""
        decisions = []
        
        for name, healthy in state['services'].items():
            if not healthy:
                # 从学习历史中找最佳策略
                best_strategy = self.get_best_strategy(name)
                
                decisions.append({
                    'problem': f'{name}_down',
                    'strategy': best_strategy['name'],
                    'confidence': best_strategy['success_rate'],
                    'reason': f'历史成功率 {best_strategy["success_rate"]*100:.0f}%'
                })
        
        return decisions
    
    def get_best_strategy(self, service):
        """从学习历史获取最佳策略"""
        history = [h for h in self.learning_history if h['service'] == service]
        
        if not history:
            return {'name': 'restart', 'success_rate': 0.5}
        
        # 统计各策略成功率
        strategy_stats = defaultdict(lambda: {'success': 0, 'total': 0})
        for h in history:
            strategy_stats[h['strategy']]['total'] += 1
            if h['success']:
                strategy_stats[h['strategy']]['success'] += 1
        
        # 找最佳策略
        best = None
        best_rate = 0
        for strategy, stats in strategy_stats.items():
            rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            if rate > best_rate:
                best_rate = rate
                best = {'name': strategy, 'success_rate': rate}
        
        return best if best else {'name': 'restart', 'success_rate': 0.5}
    
    def execute(self, decision):
        """执行模块"""
        print(f"⚡ 执行: {decision['problem']} -> {decision['strategy']}")
        
        start_time = time.time()
        
        if 'gateway' in decision['problem']:
            subprocess.Popen("python3 agent_gateway_web.py", shell=True, cwd="/mnt/d/clawsjoy")
        elif 'agent' in decision['problem']:
            subprocess.Popen("python3 multi_agent_service_v2.py", shell=True, cwd="/mnt/d/clawsjoy")
        elif 'doc' in decision['problem']:
            subprocess.Popen("python3 doc_generator.py", shell=True, cwd="/mnt/d/clawsjoy")
        
        duration = time.time() - start_time
        
        return {'success': True, 'duration': duration}
    
    def verify(self, problem):
        """验证模块"""
        time.sleep(5)
        
        # 重新感知
        new_state = self.perceive()
        
        if 'gateway' in problem:
            return new_state['services'].get('gateway', False)
        elif 'agent' in problem:
            return new_state['services'].get('agent', False)
        elif 'doc' in problem:
            return new_state['services'].get('doc', False)
        
        return False
    
    def learn(self, service, strategy, success):
        """学习模块 - 记录学习经验"""
        self.learning_history.append({
            'service': service,
            'strategy': strategy,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保留最近100条
        if len(self.learning_history) > 100:
            self.learning_history = self.learning_history[-100:]
        
        # 记录到大脑核心
        brain_core.record_experience(
            agent="closed_loop",
            action=f"learn_{service}_{strategy}",
            result={"success": success},
            context=json.dumps({'strategy': strategy})
        )
        
        if success:
            print(f"📚 学习成功: {strategy} 策略有效")
        else:
            print(f"📚 学习: {strategy} 策略失败，下次换策略")
    
    def run_cycle(self):
        """运行一个完整闭环"""
        self.loop_count += 1
        
        print(f"\n{'='*50}")
        print(f"🔄 闭环周期 #{self.loop_count}")
        print(f"{'='*50}")
        
        # 1. 感知
        state = self.perceive()
        healthy_count = sum(state['services'].values())
        print(f"📡 感知: {healthy_count}/3 服务正常")
        
        # 2. 决策
        decisions = self.decide(state)
        
        if not decisions:
            print("✅ 状态正常，无需行动")
            return
        
        # 3-5. 执行、验证、学习
        for decision in decisions:
            service = decision['problem'].replace('_down', '')
            print(f"\n🎯 决策: 修复 {service}")
            print(f"   📋 策略: {decision['strategy']}")
            print(f"   💭 理由: {decision['reason']}")
            
            # 执行
            action_result = self.execute(decision)
            
            # 验证
            resolved = self.verify(decision['problem'])
            
            # 学习
            self.learn(service, decision['strategy'], resolved)
            
            if resolved:
                print(f"   ✅ 修复成功 ({action_result['duration']:.1f}s)")
            else:
                print(f"   ❌ 修复失败，将在下次尝试其他策略")
    
    def show_stats(self):
        """显示学习统计"""
        print("\n📊 学习统计:")
        
        # 按服务统计
        services = set(h['service'] for h in self.learning_history)
        for service in services:
            history = [h for h in self.learning_history if h['service'] == service]
            strategies = set(h['strategy'] for h in history)
            print(f"\n   {service}:")
            for strategy in strategies:
                attempts = [h for h in history if h['strategy'] == strategy]
                success_count = sum(1 for a in attempts if a['success'])
                rate = success_count / len(attempts) if attempts else 0
                print(f"      {strategy}: {success_count}/{len(attempts)} ({rate*100:.0f}%)")
    
    def run(self):
        """持续运行闭环"""
        print("\n" + "="*60)
        print("🧠 智能闭环系统 - 训练模式")
        print("="*60)
        print("感知 → 决策 → 执行 → 验证 → 学习")
        print("="*60)
        
        cycle = 0
        while self.running and cycle < 20:  # 先跑20个周期训练
            try:
                self.run_cycle()
                cycle += 1
                
                # 每5个周期显示学习统计
                if cycle % 5 == 0:
                    self.show_stats()
                
                time.sleep(60)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"闭环错误: {e}")
                time.sleep(30)
        
        self.show_stats()
        print("\n✅ 训练完成")
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    loop = IntelligentClosedLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.stop()
