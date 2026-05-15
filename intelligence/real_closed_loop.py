"""真正的智能闭环 - 有LLM决策，有多种策略，能学习"""
import time
import requests
import subprocess
import json
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class RealClosedLoop:
    """真正的闭环 - 不是mock"""
    
    def __init__(self):
        self.loop_count = 0
        self.learning_history = defaultdict(list)  # 真实学习
        self.strategies = ['restart', 'reload', 'clean_cache', 'wait']  # 多种策略
        
        # 记录开始
        print("\n" + "="*60)
        print("🧠 真实闭环系统启动")
        print("="*60)
        print(f"策略库: {self.strategies}")
        print(f"学习模式: 启用")
        print("="*60)
    
    def perceive(self):
        """感知 - 真实检测"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'health_score': 0
        }
        
        for name, port in [('gateway',5002), ('agent',5005), ('doc',5008)]:
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=2)
                healthy = resp.status_code == 200
                state['services'][name] = healthy
                print(f"  {name}: {'✅' if healthy else '❌'}")
            except Exception as e:
                state['services'][name] = False
                print(f"  {name}: ❌ ({str(e)[:30]})")
        
        state['health_score'] = sum(state['services'].values()) / len(state['services']) * 100
        return state
    
    def call_llm_for_decision(self, service, failed_attempts):
        """调用LLM做决策 - 真正的智能"""
        try:
            prompt = f"""服务 {service} 出现故障。
已尝试的策略及结果: {json.dumps(failed_attempts)}
可选策略: {self.strategies}
请选择最佳策略，只输出策略名称。"""
            
            resp = requests.post("http://localhost:11434/api/generate",
                                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                                timeout=30)
            result = resp.json().get('response', 'restart').strip().lower()
            
            # 验证返回的策略是否有效
            if result in self.strategies:
                return result
            else:
                return 'restart'
        except:
            # LLM不可用时，从历史学习
            return self.best_from_history(service)
    
    def best_from_history(self, service):
        """从历史学习最佳策略"""
        history = self.learning_history.get(service, [])
        if not history:
            return 'restart'
        
        # 统计成功率
        strategy_stats = defaultdict(lambda: {'success': 0, 'total': 0})
        for h in history:
            strategy_stats[h['strategy']]['total'] += 1
            if h['success']:
                strategy_stats[h['strategy']]['success'] += 1
        
        # 找成功率最高的
        best = 'restart'
        best_rate = 0
        for strategy, stats in strategy_stats.items():
            rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            if rate > best_rate:
                best_rate = rate
                best = strategy
        
        return best
    
    def execute(self, service, strategy):
        """执行策略 - 真实执行"""
        print(f"⚡ 执行: {service} -> {strategy}")
        
        start_time = time.time()
        success = False
        
        if strategy == 'restart':
            if service == 'gateway':
                subprocess.Popen("python3 agent_gateway_web.py", shell=True, cwd="/mnt/d/clawsjoy")
            elif service == 'agent':
                subprocess.Popen("python3 multi_agent_service_v2.py", shell=True, cwd="/mnt/d/clawsjoy")
            elif service == 'doc':
                subprocess.Popen("python3 doc_generator.py", shell=True, cwd="/mnt/d/clawsjoy")
            success = True
            
        elif strategy == 'clean_cache':
            subprocess.run("find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null", shell=True)
            success = True
            
        elif strategy == 'wait':
            time.sleep(10)
            success = True
        
        duration = time.time() - start_time
        return {'success': success, 'duration': duration}
    
    def verify(self, service):
        """验证 - 真实验证"""
        time.sleep(5)
        
        ports = {'gateway': 5002, 'agent': 5005, 'doc': 5008}
        port = ports.get(service)
        
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def learn(self, service, strategy, success, duration):
        """学习 - 真实学习"""
        self.learning_history[service].append({
            'strategy': strategy,
            'success': success,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保留最近50条
        if len(self.learning_history[service]) > 50:
            self.learning_history[service] = self.learning_history[service][-50:]
        
        # 记录到大脑核心
        brain_core.record_experience(
            agent="real_closed_loop",
            action=f"fix_{service}_{strategy}",
            result={"success": success, "duration": duration},
            context="auto_heal"
        )
        
        # 输出学习结果
        if success:
            print(f"   📚 学习成功: {strategy} 有效 ({duration:.1f}s)")
        else:
            print(f"   📚 学习: {strategy} 无效，记录失败")
        
        return success
    
    def show_learning_stats(self):
        """显示学习统计"""
        print("\n" + "="*60)
        print("📊 学习统计")
        print("="*60)
        
        for service, history in self.learning_history.items():
            if not history:
                continue
            
            print(f"\n{service.upper()}:")
            
            # 统计各策略
            strategy_stats = defaultdict(lambda: {'success': 0, 'total': 0, 'avg_time': 0})
            for h in history:
                strategy_stats[h['strategy']]['total'] += 1
                if h['success']:
                    strategy_stats[h['strategy']]['success'] += 1
                    strategy_stats[h['strategy']]['avg_time'] += h['duration']
            
            for strategy, stats in strategy_stats.items():
                rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
                avg_time = stats['avg_time'] / stats['success'] if stats['success'] > 0 else 0
                print(f"   {strategy}: {stats['success']}/{stats['total']} ({rate*100:.0f}%) 平均{avg_time:.1f}s")
    
    def run_cycle(self):
        """运行一个周期"""
        self.loop_count += 1
        
        print(f"\n{'='*60}")
        print(f"🔄 周期 #{self.loop_count}")
        print(f"{'='*60}")
        
        print("\n📡 感知中...")
        state = self.perceive()
        
        if state['health_score'] == 100:
            print(f"\n✅ 所有服务正常 (健康度: {state['health_score']:.0f}%)")
            return {'action': 'none', 'health_score': state['health_score']}
        
        # 找出故障服务
        failed = [name for name, healthy in state['services'].items() if not healthy]
        
        results = []
        for service in failed:
            print(f"\n⚠️ 发现故障: {service}")
            
            # 获取该服务的失败历史
            history = self.learning_history.get(service, [])
            failed_attempts = [h for h in history if not h['success']][-3:]
            
            # LLM决策
            strategy = self.call_llm_for_decision(service, failed_attempts)
            print(f"🤔 LLM决策: 使用 {strategy} 策略")
            
            # 执行
            exec_result = self.execute(service, strategy)
            
            # 验证
            resolved = self.verify(service)
            
            # 学习
            self.learn(service, strategy, resolved, exec_result['duration'])
            
            results.append({
                'service': service,
                'strategy': strategy,
                'resolved': resolved
            })
        
        return {'action': 'fixed', 'results': results}
    
    def run(self, cycles=10):
        """运行闭环"""
        print("\n开始闭环训练...")
        print("="*60)
        
        for cycle in range(cycles):
            result = self.run_cycle()
            
            if cycle % 3 == 0 and cycle > 0:
                self.show_learning_stats()
            
            if cycle < cycles - 1:
                print(f"\n等待60秒后进行下一周期...")
                time.sleep(60)
        
        self.show_learning_stats()
        print("\n✅ 训练完成")
        print(f"📈 学习记录: {sum(len(v) for v in self.learning_history.values())} 条")

if __name__ == "__main__":
    loop = RealClosedLoop()
    loop.run(cycles=10)
