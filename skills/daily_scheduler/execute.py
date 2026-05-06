#!/usr/bin/env python3
"""每日调度器 - 自动执行完整工作流"""
import sys, json, subprocess
from datetime import datetime

def execute(params):
    workflow = params.get("workflow", "hk_daily")
    
    print(f"🚀 启动每日工作流: {workflow}")
    print(f"⏰ 时间: {datetime.now()}")
    
    # 调用 workflow_engine
    cmd = ["python3", "skills/workflow_engine.py", f"workflows/{workflow}.json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        "success": result.returncode == 0,
        "workflow": workflow,
        "output": result.stdout,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
