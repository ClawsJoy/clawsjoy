"""主动学习智能体 - 自动尝试、自我评分、主动求助"""
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

class ActiveLearner:
    """主动学习智能体"""
    
    def __init__(self):
        self.scores = defaultdict(lambda: {'success': 0, 'fail': 0, 'last_score': 0})
        self.learning_log = Path("logs/active_learning.log")
        self.help_requests = []
        
        # 从大脑加载历史分数
        self.load_scores()
        
        print("\n" + "="*60)
        print("🧠 主动学习智能体已启动")
        print("="*60)
        print("规则: 修复成功 +1分，失败 0分")
        print("求助: 连续3次失败自动求助")
        print("="*60)
    
    def load_scores(self):
        """加载历史分数"""
        experiences = brain_core.knowledge.get('experiences', [])
        for exp in experiences:
            if exp.get('agent') == 'active_learner':
                action = exp.get('action', '')
                result = exp.get('result', {})
                if 'fix_' in action:
                    fault_type = action.replace('fix_', '')
                    success = result.get('success', False)
                    if success:
                        self.scores[fault_type]['success'] += 1
                    else:
                        self.scores[fault_type]['fail'] += 1
                    self.scores[fault_type]['last_score'] = result.get('score', 0)
        
        total = sum(len(v) for v in self.scores.values())
        print(f"📚 加载历史: {total} 条评分记录")
    
    def save_score(self, fault_type, success, duration):
        """保存分数（1分成功，0分失败）"""
        score = 1 if success else 0
        
        # 更新本地统计
        if success:
            self.scores[fault_type]['success'] += 1
        else:
            self.scores[fault_type]['fail'] += 1
        self.scores[fault_type]['last_score'] = score
        
        # 计算成功率
        total = self.scores[fault_type]['success'] + self.scores[fault_type]['fail']
        rate = self.scores[fault_type]['success'] / total if total > 0 else 0
        
        # 记录到大脑
        brain_core.record_experience(
            agent="active_learner",
            action=f"fix_{fault_type}",
            result={
                "success": success,
                "score": score,
                "duration": duration,
                "success_rate": rate
            },
            context=f"total_{total}"
        )
        
        # 写入日志
        with open(self.learning_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {fault_type} | {'✅' if success else '❌'} | 得分:{score} | 成功率:{rate:.0%}\n")
        
        print(f"   📊 得分: {score}/1 | {fault_type} 成功率 {rate:.0%} ({self.scores[fault_type]['success']}/{total})")
        
        return score
    
    def need_help(self, fault_type):
        """判断是否需要求助"""
        recent_fails = 0
        experiences = brain_core.knowledge.get('experiences', [])
        
        # 检查最近3次修复
        for exp in reversed(experiences[-10:]):
            if exp.get('agent') == 'active_learner' and fault_type in exp.get('action', ''):
                success = exp.get('result', {}).get('success', False)
                if not success:
                    recent_fails += 1
                else:
                    recent_fails = 0
                if recent_fails >= 3:
                    return True
        
        return False
    
    def send_help_signal(self, fault_type, context):
        """发送求助信号"""
        signal = {
            'timestamp': datetime.now().isoformat(),
            'fault_type': fault_type,
            'context': context,
            'attempts': self.scores[fault_type]['fail'] + self.scores[fault_type]['success'],
            'success_rate': self.get_success_rate(fault_type)
        }
        self.help_requests.append(signal)
        
        # 保存求助记录
        help_file = Path("data/help_requests.json")
        with open(help_file, 'w') as f:
            json.dump(self.help_requests[-20:], f, indent=2)
        
        print(f"\n🆘 求助信号!")
        print(f"   问题: {fault_type}")
        print(f"   已尝试: {signal['attempts']} 次")
        print(f"   成功率: {signal['success_rate']:.0%}")
        print(f"   时间: {signal['timestamp']}")
        print(f"\n💡 请手动介入解决问题，或提供新的解决方案")
        
        return signal
    
    def get_success_rate(self, fault_type):
        """获取成功率"""
        total = self.scores[fault_type]['success'] + self.scores[fault_type]['fail']
        return self.scores[fault_type]['success'] / total if total > 0 else 0
    
    def try_fix(self, fault_type, fix_func):
        """尝试修复（自动评分）"""
        print(f"\n🔧 尝试修复: {fault_type}")
        
        start = time.time()
        success = fix_func()
        duration = time.time() - start
        
        # 自动评分
        score = self.save_score(fault_type, success, duration)
        
        # 检查是否需要求助
        if not success and self.need_help(fault_type):
            self.send_help_signal(fault_type, f"连续失败3次")
        
        return success, score

# 真实修复函数
class RealFixes:
    @staticmethod
    def fix_port_conflict(port):
        """修复端口冲突"""
        result = subprocess.run(f"fuser -k {port}/tcp 2>/dev/null", shell=True)
        time.sleep(1)
        check = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
        return not check.stdout.strip()
    
    @staticmethod
    def restart_service(name, port, cmd):
        """重启服务"""
        subprocess.run(f"pkill -f '{cmd.split()[-1]}'", shell=True)
        time.sleep(2)
        subprocess.Popen(cmd, shell=True, cwd="/mnt/d/clawsjoy")
        time.sleep(3)
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    @staticmethod
    def fix_ollama():
        """修复Ollama"""
        subprocess.run("pkill -f ollama", shell=True)
        time.sleep(2)
        subprocess.Popen("ollama serve > /dev/null 2>&1 &", shell=True)
        time.sleep(5)
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=5)
            return resp.status_code == 200
        except:
            return False

class ActiveLearningLoop:
    """主动学习循环"""
    
    def __init__(self):
        self.learner = ActiveLearner()
        self.fixes = RealFixes()
        self.loop_count = 0
        
        # 真实服务配置
        self.services = {
            'gateway': {'port': 5002, 'cmd': 'python3 agent_gateway_web.py'},
            'agent': {'port': 5005, 'cmd': 'python3 multi_agent_service_v2.py'},
            'doc': {'port': 5008, 'cmd': 'python3 doc_generator.py'}
        }
    
    def detect_and_learn(self):
        """检测并主动学习"""
        self.loop_count += 1
        
        print(f"\n{'='*50}")
        print(f"🔄 主动学习周期 #{self.loop_count}")
        print(f"{'='*50}")
        
        # 检测并修复每个服务
        for name, config in self.services.items():
            try:
                resp = requests.get(f"http://localhost:{config['port']}/health", timeout=3)
                if resp.status_code != 200:
                    print(f"\n⚠️ {name} 故障 (HTTP {resp.status_code})")
                    self.learner.try_fix(
                        f"service_{name}",
                        lambda: self.fixes.restart_service(name, config['port'], config['cmd'])
                    )
            except requests.exceptions.ConnectionError:
                print(f"\n⚠️ {name} 连接失败")
                self.learner.try_fix(
                    f"service_{name}",
                    lambda: self.fixes.restart_service(name, config['port'], config['cmd'])
                )
            except Exception as e:
                print(f"\n⚠️ {name} 异常: {str(e)[:50]}")
        
        # 检测端口冲突
        for port in [5002, 5005, 5008]:
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
            if result.stdout.strip():
                print(f"\n⚠️ 端口 {port} 冲突")
                self.learner.try_fix(
                    f"port_{port}",
                    lambda p=port: self.fixes.fix_port_conflict(p)
                )
        
        # 显示求助队列
        if self.learner.help_requests:
            print(f"\n📢 待处理求助: {len(self.learner.help_requests)} 个")
        
        # 每10个周期输出统计
        if self.loop_count % 10 == 0:
            self.show_stats()
    
    def show_stats(self):
        """显示统计"""
        print("\n" + "="*50)
        print("📊 学习统计")
        print("="*50)
        for fault_type, stats in self.learner.scores.items():
            total = stats['success'] + stats['fail']
            if total > 0:
                rate = stats['success'] / total
                bar = "█" * int(rate * 20)
                print(f"{fault_type}: {bar} {rate:.0%} ({stats['success']}/{total})")
    
    def run(self):
        """持续运行"""
        print("\n🚀 主动学习系统运行中...")
        print("每30秒检测一次，自动评分，失败3次自动求助\n")
        
        try:
            while True:
                self.detect_and_learn()
                print(f"\n⏳ 等待30秒...")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n停止")
            self.show_stats()
            if self.learner.help_requests:
                print(f"\n📢 未处理的求助: {len(self.learner.help_requests)}")

if __name__ == "__main__":
    loop = ActiveLearningLoop()
    loop.run()
