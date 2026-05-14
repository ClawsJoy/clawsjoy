import sys
sys.path.insert(0, "/mnt/d/clawsjoy")
#!/usr/bin/env python3
"""性能分析 - 分析各模块执行效率"""
import subprocess
import re
from lib.memory_simple import memory
from datetime import datetime

def analyze_response_times():
    """分析API响应时间"""
    result = subprocess.run("grep -E 'POST|GET' logs/gateway.log | tail -100 | grep -oE '[0-9]+ms' | sed 's/ms//'", 
                           shell=True, capture_output=True, text=True)
    times = [int(t) for t in result.stdout.strip().split('\n') if t]
    if times:
        avg = sum(times) / len(times)
        max_t = max(times)
        return avg, max_t
    return 0, 0

def analyze_memory_usage():
    """分析内存使用"""
    result = subprocess.run("ps aux | grep python | awk '{sum+=$6} END {print sum/1024}'", 
                           shell=True, capture_output=True, text=True)
    mem_mb = float(result.stdout.strip()) if result.stdout.strip() else 0
    return mem_mb

def main():
    avg_time, max_time = analyze_response_times()
    mem_usage = analyze_memory_usage()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "avg_response_ms": avg_time,
        "max_response_ms": max_time,
        "memory_usage_mb": mem_usage,
        "health_score": 100 if avg_time < 100 else (70 if avg_time < 500 else 30)
    }
    
    memory.remember(
        f"性能报告|平均响应:{avg_time:.0f}ms|最大:{max_time}ms|内存:{mem_usage:.0f}MB",
        category="performance_metrics"
    )
    
    print(f"📊 性能报告: 平均响应{avg_time:.0f}ms, 内存{mem_usage:.0f}MB")

if __name__ == "__main__":
    main()
