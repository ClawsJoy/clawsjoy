"""智能学习器 - 从经验中自动优化"""
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class IntelligentLearner:
    def __init__(self):
        self.learning_log = Path("logs/learning.log")
        self.learning_log.parent.mkdir(parents=True, exist_ok=True)
        
    def analyze_experiences(self):
        """分析经验，提取模式"""
        stats = brain.get_stats()
        
        insights = []
        
        # 分析成功率趋势
        success_rate = stats.get('success_rate', 0)
        if success_rate < 0.7:
            insights.append({
                "type": "warning",
                "message": f"成功率偏低 ({success_rate*100:.0f}%)",
                "suggestion": "建议增加训练数据或调整策略"
            })
        elif success_rate > 0.9:
            insights.append({
                "type": "success", 
                "message": f"成功率优秀 ({success_rate*100:.0f}%)",
                "suggestion": "继续保持当前策略"
            })
        
        # 分析知识图谱
        kg_nodes = stats.get('knowledge_graph_nodes', 0)
        if kg_nodes < 20:
            insights.append({
                "type": "info",
                "message": f"知识图谱较小 ({kg_nodes}个节点)",
                "suggestion": "多使用不同功能来扩展知识"
            })
        
        return insights
    
    def auto_optimize(self):
        """自动优化建议"""
        insights = self.analyze_experiences()
        
        for insight in insights:
            print(f"📚 {insight['type'].upper()}: {insight['message']}")
            print(f"   💡 {insight['suggestion']}")
            
            # 记录到大脑
            brain.record_experience(
                agent="learner",
                action="auto_optimize",
                result={"insight": insight},
                context=insight['suggestion']
            )
        
        # 保存学习日志
        with open(self.learning_log, 'a') as f:
            f.write(f"{datetime.now()}: {json.dumps(insights)}\n")
        
        return insights

if __name__ == "__main__":
    learner = IntelligentLearner()
    learner.auto_optimize()
