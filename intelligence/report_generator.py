"""智能报告生成器"""
import json
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class ReportGenerator:
    def generate(self):
        stats = brain.get_stats()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "brain": {
                "experiences": stats.get('total_experiences', 0),
                "success_rate": stats.get('success_rate', 0),
                "knowledge_nodes": stats.get('knowledge_graph_nodes', 0)
            }
        }
        
        with open("data/full_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "=" * 50)
        print("📊 ClawsJoy 智能报告")
        print("=" * 50)
        print(f"🧠 经验: {report['brain']['experiences']} 条")
        print(f"📈 成功率: {report['brain']['success_rate']*100:.1f}%")
        print(f"🔗 知识节点: {report['brain']['knowledge_nodes']} 个")
        print("=" * 50)
        
        return report

if __name__ == "__main__":
    gen = ReportGenerator()
    gen.generate()
