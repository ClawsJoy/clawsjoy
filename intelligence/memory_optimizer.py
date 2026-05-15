"""智能记忆优化器 - 自动整理和优化记忆"""
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class MemoryOptimizer:
    """记忆优化器"""
    
    def __init__(self):
        self.optimization_log = Path("logs/memory_optimization.log")
        
    def analyze_memory_health(self) -> dict:
        """分析记忆健康度"""
        stats = brain.get_stats()
        
        health = {
            "total_memories": stats.get('total_experiences', 0),
            "knowledge_nodes": stats.get('knowledge_graph_nodes', 0),
            "analogies": stats.get('analogies_count', 0),
            "best_practices": stats.get('best_practices', 0),
            "health_score": 0
        }
        
        # 计算健康分
        score = 0
        if health['total_memories'] > 50:
            score += 30
        elif health['total_memories'] > 20:
            score += 20
        else:
            score += 10
            
        if health['knowledge_nodes'] > 30:
            score += 30
        elif health['knowledge_nodes'] > 15:
            score += 20
        else:
            score += 10
            
        if health['best_practices'] > 5:
            score += 40
        elif health['best_practices'] > 2:
            score += 20
        else:
            score += 10
            
        health['health_score'] = score
        
        return health
    
    def suggest_optimization(self) -> list:
        """建议优化措施"""
        health = self.analyze_memory_health()
        suggestions = []
        
        if health['total_memories'] < 30:
            suggestions.append("记忆不足，建议多使用系统功能积累经验")
        
        if health['knowledge_nodes'] < 20:
            suggestions.append("知识图谱较小，建议使用不同功能扩展知识")
        
        if health['best_practices'] < 3:
            suggestions.append("最佳实践较少，系统还在学习初期")
        
        return suggestions
    
    def optimize(self):
        """执行优化"""
        health = self.analyze_memory_health()
        suggestions = self.suggest_optimization()
        
        print("🧠 记忆优化报告")
        print("=" * 50)
        print(f"📊 记忆健康度: {health['health_score']}/100")
        print(f"📚 总记忆: {health['total_memories']}")
        print(f"🔗 知识节点: {health['knowledge_nodes']}")
        print(f"🎯 类比数: {health['analogies']}")
        print(f"⭐ 最佳实践: {health['best_practices']}")
        
        if suggestions:
            print(f"\n💡 优化建议:")
            for s in suggestions:
                print(f"   • {s}")
        
        # 记录优化日志
        with open(self.optimization_log, 'a') as f:
            f.write(f"{datetime.now()}: {json.dumps(health)}\n")
        
        return health

if __name__ == "__main__":
    optimizer = MemoryOptimizer()
    optimizer.optimize()
