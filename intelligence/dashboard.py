"""统一智能仪表盘"""
import json
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from intelligence.log_analyzer import LogAnalyzer
from intelligence.performance_monitor import PerformanceMonitor
from intelligence.recommendation_engine import RecommendationEngine
from agent_core.brain_enhanced import brain

class IntelligentDashboard:
    def __init__(self):
        self.log_analyzer = LogAnalyzer()
        self.performance_monitor = PerformanceMonitor()
        self.recommendation_engine = RecommendationEngine()
    
    def display(self):
        """显示完整仪表盘"""
        print("\n" + "=" * 60)
        print("🧠 ClawsJoy 智能仪表盘")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 大脑状态
        stats = brain.get_stats()
        print(f"\n📊 大脑状态:")
        print(f"   经验: {stats.get('total_experiences', 0)} 条")
        print(f"   成功率: {stats.get('success_rate', 0)*100:.1f}%")
        print(f"   知识节点: {stats.get('knowledge_graph_nodes', 0)} 个")
        print(f"   类比库: {stats.get('analogies_count', 0)} 条")
        print(f"   最佳实践: {stats.get('best_practices', 0)} 条")
        
        # 性能指标
        self.performance_monitor.generate_report()
        
        # 日志分析
        self.log_analyzer.generate_report()
        
        # 智能推荐
        self.recommendation_engine.generate_report()
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    dashboard = IntelligentDashboard()
    dashboard.display()

# 添加备份和配置信息
def display_extra(self):
    from intelligence.backup_manager import BackupManager
    from intelligence.config_manager import ConfigManager
    
    backup_manager = BackupManager()
    backups = backup_manager.list_backups()
    print(f"\n💾 备份信息:")
    print(f"   总备份数: {len(backups)}")
    if backups:
        latest = backups[-1]
        print(f"   最新备份: {latest['name']} ({latest['size']})")
    
    config_manager = ConfigManager()
    print(f"\n⚙️ 智能配置:")
    print(f"   自动备份: {'开启' if config_manager.get('auto_backup') else '关闭'}")
    print(f"   自动修复: {'开启' if config_manager.get('auto_heal') else '关闭'}")
    print(f"   学习率: {config_manager.get('learning_rate')}")
