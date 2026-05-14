"""性能监控器 - 监控系统性能指标"""
import time
import psutil
import json
from pathlib import Path
from datetime import datetime
from collections import deque
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class PerformanceMonitor:
    def __init__(self):
        self.history = deque(maxlen=100)
        self.metrics_file = Path("data/performance_metrics.json")
        
    def collect_metrics(self):
        """收集当前指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count()
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'used_gb': psutil.virtual_memory().used / (1024**3),
                'total_gb': psutil.virtual_memory().total / (1024**3)
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'free_gb': psutil.disk_usage('/').free / (1024**3)
            },
            'processes': len(psutil.pids())
        }
        
        self.history.append(metrics)
        return metrics
    
    def check_thresholds(self, metrics):
        """检查阈值告警"""
        alerts = []
        
        if metrics['cpu']['percent'] > 80:
            alerts.append(f"CPU 使用率过高: {metrics['cpu']['percent']}%")
        if metrics['memory']['percent'] > 80:
            alerts.append(f"内存使用率过高: {metrics['memory']['percent']}%")
        if metrics['disk']['percent'] > 85:
            alerts.append(f"磁盘使用率过高: {metrics['disk']['percent']}%")
            
        return alerts
    
    def get_trend(self):
        """获取趋势分析"""
        if len(self.history) < 10:
            return None
            
        recent = list(self.history)[-10:]
        cpu_trend = recent[-1]['cpu']['percent'] - recent[0]['cpu']['percent']
        mem_trend = recent[-1]['memory']['percent'] - recent[0]['memory']['percent']
        
        return {
            'cpu_trend': '上升' if cpu_trend > 5 else '下降' if cpu_trend < -5 else '稳定',
            'memory_trend': '上升' if mem_trend > 5 else '下降' if mem_trend < -5 else '稳定'
        }
    
    def generate_report(self):
        """生成性能报告"""
        metrics = self.collect_metrics()
        alerts = self.check_thresholds(metrics)
        trend = self.get_trend()
        
        print("\n📈 性能监控报告")
        print("=" * 50)
        print(f"🖥️ CPU: {metrics['cpu']['percent']}% ({metrics['cpu']['cores']} 核心)")
        print(f"💾 内存: {metrics['memory']['percent']}% ({metrics['memory']['used_gb']:.1f}/{metrics['memory']['total_gb']:.1f} GB)")
        print(f"💿 磁盘: {metrics['disk']['percent']}% (剩余 {metrics['disk']['free_gb']:.1f} GB)")
        
        if trend:
            print(f"\n📊 趋势: CPU {trend['cpu_trend']}, 内存 {trend['memory_trend']}")
        
        if alerts:
            print(f"\n⚠️ 告警:")
            for alert in alerts:
                print(f"   {alert}")
        else:
            print(f"\n✅ 所有指标正常")
        
        # 保存指标
        with open(self.metrics_file, 'w') as f:
            json.dump(list(self.history)[-50:], f, indent=2)
        
        return metrics

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.generate_report()
