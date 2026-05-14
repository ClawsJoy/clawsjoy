"""智能分析器 - 分析系统状态，提供洞察"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class IntelligenceAnalyzer:
    def __init__(self):
        self.report_file = Path("data/intelligence_report.json")
    
    def analyze(self):
        stats = brain.get_stats()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": self._calc_health_score(stats),
            "insights": [],
            "recommendations": []
        }
        
        # 健康度评分
        report["health_score"] = int(stats['success_rate'] * 100)
        
        # 洞察
        if stats['total_experiences'] > 100:
            report["insights"].append("经验丰富，系统已成熟")
        elif stats['total_experiences'] > 50:
            report["insights"].append("经验中等，继续使用会更好")
        else:
            report["insights"].append("经验较少，多使用可提升效果")
        
        if stats['success_rate'] > 0.9:
            report["insights"].append("成功率很高，系统稳定")
        elif stats['success_rate'] > 0.7:
            report["insights"].append("成功率良好，有提升空间")
        else:
            report["insights"].append("成功率偏低，需要优化")
        
        # 建议
        if stats['knowledge_graph_nodes'] < 30:
            report["recommendations"].append("知识图谱节点较少，建议多使用不同功能")
        
        if stats['best_practices'] < 5:
            report["recommendations"].append("最佳实践较少，系统还在学习阶段")
        
        # 保存报告
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _calc_health_score(self, stats):
        score = int(stats['success_rate'] * 70)
        score += min(20, stats['total_experiences'] // 5)
        score += min(10, stats['knowledge_graph_nodes'] // 5)
        return min(100, score)
    
    def print_report(self):
        report = self.analyze()
        print("\n" + "="*50)
        print("📊 ClawsJoy 智能分析报告")
        print("="*50)
        print(f"🩺 健康度: {report['health_score']}/100")
        print(f"\n💡 洞察:")
        for i in report['insights']:
            print(f"   • {i}")
        print(f"\n📋 建议:")
        for r in report['recommendations']:
            print(f"   • {r}")
        print("="*50)

if __name__ == '__main__':
    analyzer = IntelligenceAnalyzer()
    analyzer.print_report()
