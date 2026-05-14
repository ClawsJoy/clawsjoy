#!/usr/bin/env python3
"""异常预测 - 分析日志预测潜在故障"""
import subprocess
import re
from datetime import datetime

def analyze_logs():
    # 获取最近错误
    result = subprocess.run("tail -200 logs/gateway.log | grep -i error | wc -l", 
                           shell=True, capture_output=True, text=True)
    error_count = int(result.stdout.strip())
    
    if error_count > 10:
        return f"⚠️ 警告: 最近有{error_count}个错误，建议检查"
    elif error_count > 5:
        return f"⚠️ 注意: 最近有{error_count}个错误"
    return "✅ 正常"

if __name__ == "__main__":
    status = analyze_logs()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {status}")
