"""智能推荐引擎 - 根据系统状态推荐优化措施"""
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class RecommendationEngine:
    def __init__(self):
        self.recommendations_file = Path("data/recommendations.json")
        
    def analyze_and_recommend(self):
        """分析并生成推荐"""
        stats = brain.get_stats()
        
        recommendations = []
        
        # 基于经验数量的推荐
        experiences = stats.get('total_experiences', 0)
        if experiences < 30:
            recommendations.append({
                'type': 'learning',
                'priority': 'high',
                'title': '增加系统使用',
                'description': '当前经验较少，多使用系统功能可以提升智能水平',
                'action': '使用各种技能和功能'
            })
        
        # 基于成功率的推荐
        success_rate = stats.get('success_rate', 0)
        if success_rate < 0.7:
            recommendations.append({
                'type': 'optimization',
                'priority': 'high',
                'title': '优化执行策略',
                'description': f'当前成功率 {success_rate*100:.0f}%，需要优化',
                'action': '检查失败记录，调整策略'
            })
        
        # 基于知识图谱的推荐
        kg_nodes = stats.get('knowledge_graph_nodes', 0)
        if kg_nodes < 30:
            recommendations.append({
                'type': 'exploration',
                'priority': 'medium',
                'title': '扩展知识图谱',
                'description': f'知识节点 {kg_nodes} 个，建议增加多样性',
                'action': '探索不同类型的功能'
            })
        
        # 基于最佳实践的推荐
        best_practices = stats.get('best_practices', 0)
        if best_practices < 5:
            recommendations.append({
                'type': 'learning',
                'priority': 'low',
                'title': '积累最佳实践',
                'description': '最佳实践较少，系统还在学习阶段',
                'action': '持续使用系统会自动学习'
            })
        
        return recommendations
    
    def generate_report(self):
        """生成推荐报告"""
        recommendations = self.analyze_and_recommend()
        
        print("\n💡 智能推荐报告")
        print("=" * 50)
        
        if not recommendations:
            print("✅ 系统状态良好，暂无优化建议")
        else:
            for rec in recommendations:
                priority_icon = '🔴' if rec['priority'] == 'high' else '🟡' if rec['priority'] == 'medium' else '🟢'
                print(f"\n{priority_icon} [{rec['priority'].upper()}] {rec['title']}")
                print(f"   📝 {rec['description']}")
                print(f"   🎯 建议: {rec['action']}")
        
        # 保存推荐
        with open(self.recommendations_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'recommendations': recommendations
            }, f, indent=2)
        
        return recommendations

if __name__ == "__main__":
    engine = RecommendationEngine()
    engine.generate_report()
