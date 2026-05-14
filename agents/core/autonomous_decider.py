"""自主决策引擎 - 让系统自己决定做什么"""

import random
import requests
from datetime import datetime
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
from agents.core.predictor import predictor
from agents.core.active_explorer import active_explorer

class AutonomousDecider:
    def __init__(self):
        self.goals = [
            "提升系统性能",
            "学习新技能",
            "优化响应速度",
            "减少错误率",
            "探索未使用功能"
        ]
        self.decision_log = []
    
    def sense(self):
        """感知当前状态"""
        stats = brain.get_stats()
        
        # 收集系统信息
        context = {
            "success_rate": stats.get('success_rate', 0),
            "total_experiences": stats.get('total_experiences', 0),
            "knowledge_graph_size": stats.get('knowledge_graph_nodes', 0),
            "time": datetime.now().isoformat()
        }
        
        # 找出薄弱点
        if stats.get('success_rate', 1) < 0.7:
            context["need_improvement"] = "成功率偏低，需要优化"
        elif stats.get('total_experiences', 0) < 20:
            context["need_improvement"] = "经验不足，需要更多学习"
        else:
            context["need_improvement"] = None
        
        return context
    
    def decide(self, context):
        """决定下一步做什么"""
        decisions = []
        
        # 基于上下文做决策
        if context.get("need_improvement") == "成功率偏低，需要优化":
            decisions.append({
                "action": "reflect",
                "reason": "成功率低，需要反思",
                "priority": "high"
            })
        
        if context.get("need_improvement") == "经验不足，需要更多学习":
            decisions.append({
                "action": "explore",
                "reason": "经验不足，主动探索",
                "priority": "high"
            })
        
        # 定期维护
        if random.random() < 0.3:
            decisions.append({
                "action": "optimize",
                "reason": "定期优化",
                "priority": "medium"
            })
        
        if not decisions:
            # 默认：测试一个未使用的技能
            decisions.append({
                "action": "test_random",
                "reason": "探索未知",
                "priority": "low"
            })
        
        return decisions
    
    def execute_decision(self, decision):
        """执行决策"""
        action = decision.get("action")
        print(f"🎯 执行决策: {action} - {decision.get('reason')}")
        
        if action == "reflect":
            from agents.core.reflection_engine import reflection_engine
            result = reflection_engine.reflect()
            return result
        
        elif action == "explore":
            result = active_explorer.explore(rounds=2)
            return result
        
        elif action == "optimize":
            # 执行优化：清理旧数据、重建索引等
            result = self._optimize()
            return result
        
        elif action == "test_random":
            result = self._test_random()
            return result
        
        return {"success": False, "error": f"Unknown action: {action}"}
    
    def _optimize(self):
        """系统优化"""
        print("🔧 执行系统优化...")
        # 清理旧日志
        import subprocess
        subprocess.run("find /mnt/d/clawsjoy/logs -name '*.log' -mtime +7 -delete", shell=True)
        
        # 记录优化
        brain.record_experience(
            agent="autonomous_decider",
            action="系统优化",
            result={"success": True},
            context="auto_optimize"
        )
        return {"success": True, "action": "optimize"}
    
    def _test_random(self):
        """随机测试一个功能 - 简化版"""
        from skills.skill_interface import skill_registry
        skills = skill_registry.get_skill_names()
        if skills:
            import random
            test_skill = random.choice(skills[:10])
            print(f"🧪 随机测试: {test_skill}")
            
            skill = skill_registry.get(test_skill)
            if skill:
                try:
                    result = skill.execute({"test": True})
                    brain.record_experience(
                        agent="autonomous_decider",
                        action=f"随机测试_{test_skill}",
                        result={"success": result.get('success', False)},
                        context="auto_test"
                    )
                    return {"success": True, "tested": test_skill, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "No skills available"}
    
    def run_cycle(self):
        """运行一个自主决策周期"""
        print("\n" + "="*60)
        print("🧠 自主决策周期")
        print("="*60)
        
        # 1. 感知
        context = self.sense()
        print(f"📊 当前状态: 成功率={context['success_rate']:.1%}, 经验={context['total_experiences']}")
        
        # 2. 决策
        decisions = self.decide(context)
        print(f"📋 生成 {len(decisions)} 个决策")
        
        # 3. 执行
        results = []
        for decision in decisions:
            result = self.execute_decision(decision)
            results.append(result)
            brain.record_experience(
                agent="autonomous_decider",
                action=decision.get("action"),
                result={"success": result.get('success', False)},
                context=decision.get("reason")
            )
        
        # 4. 记录决策历史
        self.decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "decisions": decisions,
            "results": results
        })
        
        return {"context": context, "decisions": decisions, "results": results}
    
    def get_stats(self):
        return {
            "total_decisions": len(self.decision_log),
            "recent_decisions": self.decision_log[-3:] if self.decision_log else []
        }

autonomous_decider = AutonomousDecider()

if __name__ == '__main__':
    result = autonomous_decider.run_cycle()
    print(f"\n📊 决策结果: {result.get('context')}")
