"""资源优化器 - 监控和优化系统资源"""

import subprocess
import psutil
import time
from datetime import datetime
from pathlib import Path
import json
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class ResourceOptimizer:
    def __init__(self):
        self.metrics = []
        self.optimization_log = Path("data/optimization_log.json")
        self.thresholds = {
            "cpu_warning": 70,
            "cpu_critical": 85,
            "memory_warning": 80,
            "memory_critical": 90,
            "disk_warning": 80,
            "disk_critical": 90
        }
        self._load_log()
    
    def _load_log(self):
        if self.optimization_log.exists():
            with open(self.optimization_log, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {"optimizations": [], "metrics": []}
    
    def _save_log(self):
        with open(self.optimization_log, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def collect_metrics(self):
        """采集资源指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids())
        }
        
        self.metrics.append(metrics)
        self.history["metrics"].append(metrics)
        self.history["metrics"] = self.history["metrics"][-100:]
        self._save_log()
        
        return metrics
    
    def analyze_resources(self):
        """分析资源使用"""
        metrics = self.collect_metrics()
        issues = []
        
        if metrics['cpu_percent'] > self.thresholds['cpu_warning']:
            issues.append(f"CPU 使用率 {metrics['cpu_percent']}%")
        if metrics['memory_percent'] > self.thresholds['memory_warning']:
            issues.append(f"内存使用率 {metrics['memory_percent']}%")
        if metrics['disk_percent'] > self.thresholds['disk_warning']:
            issues.append(f"磁盘使用率 {metrics['disk_percent']}%")
        
        return {"metrics": metrics, "issues": issues}
    
    def optimize(self):
        """执行优化"""
        print("\n" + "="*50)
        print("⚡ 资源优化")
        print("="*50)
        
        analysis = self.analyze_resources()
        metrics = analysis['metrics']
        issues = analysis['issues']
        
        print(f"📊 CPU: {metrics['cpu_percent']}% | 内存: {metrics['memory_percent']}% | 磁盘: {metrics['disk_percent']}%")
        
        optimizations = []
        
        # CPU 优化
        if metrics['cpu_percent'] > self.thresholds['cpu_critical']:
            print("🔧 CPU 过高，清理进程...")
            result = subprocess.run("pkill -f 'python.*test' 2>/dev/null", shell=True)
            optimizations.append({"type": "cpu", "action": "kill_test_processes"})
        
        # 内存优化
        if metrics['memory_percent'] > self.thresholds['memory_critical']:
            print("🔧 内存过高，清理缓存...")
            result = subprocess.run("sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null", shell=True)
            optimizations.append({"type": "memory", "action": "clear_cache"})
        
        # 磁盘优化
        if metrics['disk_percent'] > self.thresholds['disk_critical']:
            print("🔧 磁盘不足，清理日志...")
            subprocess.run("find /mnt/d/clawsjoy/logs -name '*.log' -mtime +3 -delete", shell=True)
            optimizations.append({"type": "disk", "action": "clean_logs"})
        
        if optimizations:
            brain.record_experience(
                agent="resource_optimizer",
                action="资源优化",
                result={"success": True, "optimizations": optimizations},
                context=f"CPU={metrics['cpu_percent']}%"
            )
            print(f"✅ 已执行 {len(optimizations)} 项优化")
        else:
            print("✅ 资源正常，无需优化")
        
        self.history["optimizations"].append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "optimizations": optimizations
        })
        self._save_log()
        
        return {"optimized": len(optimizations) > 0, "optimizations": optimizations}
    
    def get_stats(self):
        return {
            "total_optimizations": len(self.history["optimizations"]),
            "recent_metrics": self.metrics[-5:] if self.metrics else []
        }

optimizer = ResourceOptimizer()

if __name__ == '__main__':
    optimizer.optimize()
