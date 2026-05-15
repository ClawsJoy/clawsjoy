#!/usr/bin/env python3
"""异步上传任务 - 延迟执行"""

import sys
import json
import subprocess
import time
import os
from datetime import datetime

# 任务队列目录
TASK_QUEUE = "/mnt/d/clawsjoy/data/upload_queue"
os.makedirs(TASK_QUEUE, exist_ok=True)

def schedule_upload(video_path, title, delay_minutes=15, tenant_id="tenant_1"):
    """安排延迟上传任务"""
    task_id = f"upload_{int(time.time())}_{os.path.basename(video_path)}"
    task_file = f"{TASK_QUEUE}/{task_id}.json"
    execute_time = time.time() + (delay_minutes * 60)
    
    task = {
        "id": task_id,
        "video_path": video_path,
        "title": title,
        "tenant_id": tenant_id,
        "schedule_time": execute_time,
        "created_at": time.time(),
        "status": "pending"
    }
    
    with open(task_file, 'w') as f:
        json.dump(task, f, indent=2)
    
    print(f"📅 已安排上传任务，将在 {delay_minutes} 分钟后执行")
    print(f"   任务 ID: {task_id}")
    return task_id

def execute_upload(video_path, title, tenant_id="tenant_1"):
    """执行实际上传"""
    cmd = [
        "python3", "/mnt/d/clawsjoy/agents/youtube_uploader.py",
        "--tenant", tenant_id,
        "--title", title
    ]
    # 注意：youtube_uploader.py 会自动找最新视频，不需要指定 --video
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def process_queue():
    """处理任务队列（由定时任务调用）"""
    now = time.time()
    processed = []
    
    if not os.path.exists(TASK_QUEUE):
        return processed
    
    for task_file in os.listdir(TASK_QUEUE):
        if not task_file.endswith('.json'):
            continue
        
        with open(f"{TASK_QUEUE}/{task_file}", 'r') as f:
            task = json.load(f)
        
        if task["status"] != "pending":
            continue
        
        if now >= task["schedule_time"]:
            print(f"🔄 执行上传任务: {task['id']}")
            success, output = execute_upload(
                task["video_path"], 
                task["title"], 
                task.get("tenant_id", "tenant_1")
            )
            
            task["status"] = "completed" if success else "failed"
            task["completed_at"] = time.time()
            task["result"] = output
            
            with open(f"{TASK_QUEUE}/{task_file}", 'w') as f:
                json.dump(task, f, indent=2)
            
            print(f"✅ 上传{'成功' if success else '失败'}: {task['id']}")
            if success and output:
                print(f"   📺 {output}")
            processed.append(task_file)
    
    return processed

def list_queue():
    """列出待处理任务"""
    if not os.path.exists(TASK_QUEUE):
        return []
    
    tasks = []
    for task_file in os.listdir(TASK_QUEUE):
        if not task_file.endswith('.json'):
            continue
        with open(f"{TASK_QUEUE}/{task_file}", 'r') as f:
            task = json.load(f)
        tasks.append(task)
    return tasks

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "schedule":
            video = sys.argv[2] if len(sys.argv) > 2 else ""
            title = sys.argv[3] if len(sys.argv) > 3 else "ClawsJoy 视频"
            delay = int(sys.argv[4]) if len(sys.argv) > 4 else 15
            schedule_upload(video, title, delay)
        elif sys.argv[1] == "process":
            process_queue()
        elif sys.argv[1] == "list":
            tasks = list_queue()
            print(f"待处理任务数: {len(tasks)}")
            for t in tasks:
                print(f"  - {t['id']}: {t['status']}")
    else:
        print("用法:")
        print("  python3 async_upload.py schedule <视频路径> <标题> [延迟分钟]")
        print("  python3 async_upload.py process")
        print("  python3 async_upload.py list")
