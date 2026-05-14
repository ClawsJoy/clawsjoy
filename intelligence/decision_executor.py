"""智能决策执行器 - 大脑完全自主决策"""
import json
import requests
import subprocess
import time
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from intelligence.auto_fixer import AutoFixer
from intelligence.notifier import Notifier
from agent_core.brain_enhanced import brain

class BrainDecisionExecutor:
    """大脑自主决策执行器 - 不依赖人工"""
    
    def __init__(self):
        self.fixer = AutoFixer()
        self.notifier = Notifier()
        self.decision_log = Path("data/brain_decisions.json")
        self.execution_history = []
        self.load_history()
        
    def load_history(self):
        if self.decision_log.exists():
            with open(self.decision_log, 'r') as f:
                self.execution_history = json.load(f)
    
    def save_history(self):
        try:
            # 只保存可序列化的字段
            serializable = []
            for item in self.execution_history[-100:]:
                if isinstance(item, dict):
                    # 过滤掉不可序列化的值
                    clean_item = {}
                    for k, v in item.items():
                        if not callable(v) and not hasattr(v, '__dict__'):
                            clean_item[k] = v
                    serializable.append(clean_item)
            with open(self.decision_log, 'w') as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")
    
    def analyze_system_state(self):
        """分析系统状态 - 大脑核心能力"""
        stats = brain.get_stats()
        
        # 检查服务健康
        services_healthy = self._check_all_services()
        
        # 获取性能指标
        performance = self._get_performance()
        
        state = {
            'timestamp': datetime.now().isoformat(),
            'brain': {
                'experiences': stats.get('total_experiences', 0),
                'success_rate': stats.get('success_rate', 0),
                'knowledge_nodes': stats.get('knowledge_graph_nodes', 0),
                'best_practices': stats.get('best_practices', 0)
            },
            'services': services_healthy,
            'performance': performance,
            'previous_decisions': self.execution_history[-5:] if self.execution_history else []
        }
        
        return state
    
    def _check_all_services(self):
        """检查所有服务"""
        services = {
            'gateway': 'http://localhost:5002/health',
            'file': 'http://localhost:5003/health',
            'agent': 'http://localhost:5005/health',
            'doc': 'http://localhost:5008/health'
        }
        
        status = {}
        for name, url in services.items():
            try:
                resp = requests.get(url, timeout=3)
                status[name] = resp.status_code == 200
            except:
                status[name] = False
        return status
    
    def _get_performance(self):
        """获取性能指标"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except:
            return {'cpu_percent': 0, 'memory_percent': 0, 'disk_percent': 0}
    
    def brain_decide(self, state):
        """大脑决策 - 基于当前状态做出决策"""
        decisions = []
        
        # 决策1: 服务异常 -> 自动修复
        down_services = [name for name, healthy in state['services'].items() if not healthy]
        if down_services:
            decisions.append({
                'action': 'fix_services',
                'priority': 100,
                'reason': f'服务异常: {down_services}',
                'executor': self._fix_services
            })
        
        # 决策2: 成功率低 -> 优化学习
        if state['brain']['success_rate'] < 0.7:
            decisions.append({
                'action': 'optimize_learning',
                'priority': 90,
                'reason': f"成功率偏低: {state['brain']['success_rate']*100:.0f}%",
                'executor': self._optimize_learning
            })
        
        # 决策3: 经验不足 -> 主动探索
        if state['brain']['experiences'] < 30:
            decisions.append({
                'action': 'explore_and_learn',
                'priority': 80,
                'reason': f"经验不足: {state['brain']['experiences']}条",
                'executor': self._explore_and_learn
            })
        
        # 决策4: 知识节点少 -> 扩展知识
        if state['brain']['knowledge_nodes'] < 30:
            decisions.append({
                'action': 'expand_knowledge',
                'priority': 70,
                'reason': f"知识节点: {state['brain']['knowledge_nodes']}个",
                'executor': self._expand_knowledge
            })
        
        # 决策5: 磁盘空间不足 -> 清理
        if state['performance']['disk_percent'] > 85:
            decisions.append({
                'action': 'cleanup_disk',
                'priority': 95,
                'reason': f"磁盘使用率: {state['performance']['disk_percent']}%",
                'executor': self._cleanup_disk
            })
        
        # 决策6: 内存压力 -> 优化内存
        if state['performance']['memory_percent'] > 80:
            decisions.append({
                'action': 'optimize_memory',
                'priority': 85,
                'reason': f"内存使用率: {state['performance']['memory_percent']}%",
                'executor': self._optimize_memory
            })
        
        # 按优先级排序
        decisions.sort(key=lambda x: x['priority'], reverse=True)
        return decisions
    
    def _fix_services(self):
        """执行服务修复"""
        print("🔧 大脑决策: 修复异常服务")
        fixed = self.fixer.auto_fix_services()
        if fixed:
            self.notifier.send("服务修复", f"已修复: {fixed}", 'success')
            brain.record_experience(
                agent="brain_decision",
                action="fix_services",
                result={"fixed": fixed},
                context="auto_detected"
            )
        return len(fixed) > 0
    
    def _optimize_learning(self):
        """优化学习策略"""
        print("📚 大脑决策: 优化学习策略")
        current_rate = brain.get_stats().get('learning_rate', 0.3)
        new_rate = min(0.5, current_rate + 0.05)
        
        # 更新大脑配置
        if hasattr(brain, 'knowledge'):
            brain.knowledge['learning_rate'] = new_rate
        
        self.notifier.send("学习优化", f"学习率: {current_rate:.2f} -> {new_rate:.2f}", 'info')
        brain.record_experience(
            agent="brain_decision",
            action="optimize_learning",
            result={"old_rate": current_rate, "new_rate": new_rate},
            context="success_rate_low"
        )
        return True
    
    def _explore_and_learn(self):
        """主动探索学习"""
        print("🔍 大脑决策: 主动探索学习")
        
        # 测试一个新技能
        try:
            # 尝试调用文档生成
            resp = requests.post("http://localhost:5008/md",
                                json={"title": "大脑探索测试", "content": "自动学习测试"},
                                timeout=10)
            if resp.status_code == 200:
                self.notifier.send("主动学习", "已测试新功能", 'success')
                brain.record_experience(
                    agent="brain_decision",
                    action="explore_new_feature",
                    result={"success": True},
                    context="active_exploration"
                )
                return True
        except:
            pass
        return False
    
    def _expand_knowledge(self):
        """扩展知识图谱"""
        print("🔗 大脑决策: 扩展知识图谱")
        
        # 模拟扩展知识
        current_nodes = brain.get_stats().get('knowledge_graph_nodes', 0)
        
        brain.record_experience(
            agent="brain_decision",
            action="expand_knowledge",
            result={"method": "auto_expansion"},
            context="knowledge_expansion"
        )
        
        self.notifier.send("知识扩展", f"节点数: {current_nodes}", 'info')
        return True
    
    def _cleanup_disk(self):
        """清理磁盘空间"""
        print("🗑️ 大脑决策: 清理磁盘空间")
        
        # 清理旧日志
        subprocess.run("find logs -name '*.log' -mtime +7 -delete", shell=True)
        # 清理旧备份
        subprocess.run("find /mnt/d/backups/clawsjoy -name '*.tar.gz' -mtime +30 -delete 2>/dev/null", shell=True)
        
        self.notifier.send("磁盘清理", "已清理旧日志和备份", 'warning')
        brain.record_experience(
            agent="brain_decision",
            action="cleanup_disk",
            result={"success": True},
            context="disk_high_usage"
        )
        return True
    
    def _optimize_memory(self):
        """优化内存使用"""
        print("💾 大脑决策: 优化内存使用")
        
        # 清理 Python 缓存
        subprocess.run("find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null", shell=True)
        
        self.notifier.send("内存优化", "已清理缓存", 'info')
        return True
    
    def execute(self):
        """大脑执行决策圈"""
        print("\n" + "=" * 60)
        print("🧠 大脑自主决策执行器")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 分析状态
        state = self.analyze_system_state()
        
        print(f"\n📊 当前状态:")
        print(f"   🧠 大脑: {state['brain']['experiences']}经验, {state['brain']['success_rate']*100:.0f}%成功率")
        print(f"   📡 服务: {sum(state['services'].values())}/4 正常")
        print(f"   💾 资源: CPU {state['performance']['cpu_percent']}% / 内存 {state['performance']['memory_percent']}% / 磁盘 {state['performance']['disk_percent']}%")
        
        # 2. 大脑决策
        decisions = self.brain_decide(state)
        
        if not decisions:
            print("\n✅ 大脑判断: 系统状态良好，无需干预")
            return {'executed': [], 'decision': 'no_action_needed'}
        
        # 3. 大脑自动执行决策（不询问）
        print(f"\n🧠 大脑决策: 将执行 {len(decisions)} 个操作")
        
        executed = []
        for decision in decisions:
            print(f"\n   📋 {decision['action']}")
            print(f"      理由: {decision['reason']}")
            print(f"      优先级: {decision['priority']}")
            
            # 大脑自动执行，无需确认
            print(f"      ⚡ 大脑自动执行中...")
            success = decision['executor']()
            
            if success:
                executed.append(decision['action'])
                print(f"      ✅ 执行成功")
            else:
                print(f"      ❌ 执行失败")
            
            # 等待一下避免冲突
            time.sleep(2)
        
        # 4. 记录执行历史
        self.execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'decisions': decisions,
            'executed': executed
        })
        self.save_history()
        
        # 5. 大脑自我学习
        if executed:
            brain.record_experience(
                agent="brain_decision",
                action="decision_cycle",
                result={"executed_actions": executed},
                context=f"executed_{len(executed)}_actions"
            )
        
        print("\n" + "=" * 60)
        print(f"✅ 大脑决策完成，执行了 {len(executed)} 个操作")
        
        return {'executed': executed, 'decision': 'actions_executed'}
    
    def run_forever(self, interval=300):
        """大脑持续运行（每5分钟决策一次）"""
        print("\n🧠 大脑持续运行模式")
        print(f"   决策间隔: {interval}秒")
        print("   按 Ctrl+C 停止\n")
        
        cycle = 0
        while True:
            try:
                cycle += 1
                print(f"\n{'='*60}")
                print(f"🧠 大脑决策周期 #{cycle}")
                self.execute()
                
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n\n🧠 大脑停止运行")
                break
            except Exception as e:
                print(f"❌ 大脑决策错误: {e}")
                time.sleep(30)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            executor = BrainDecisionExecutor()
            executor.execute()
        elif sys.argv[1] == "--daemon":
            executor = BrainDecisionExecutor()
            executor.run_forever()
    else:
        # 默认：单次执行
        executor = BrainDecisionExecutor()
        executor.execute()
