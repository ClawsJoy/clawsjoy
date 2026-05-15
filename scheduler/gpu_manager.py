#!/usr/bin/env python3
"""GPU 资源管理器 - 支持定时任务和临时任务"""

import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from queue import Queue

GPU_QUEUE = Queue()
GPU_LOCK = Path("/mnt/d/clawsjoy/tasks/gpu.lock")
TASKS_DIR = Path("/mnt/d/clawsjoy/tasks")

class GPUManager:
    def __init__(self):
        self.running = False
        self.current_task = None
    
    def is_gpu_idle(self):
        """检查 GPU 是否空闲"""
        # 检查锁文件
        if GPU_LOCK.exists():
            try:
                pid = int(GPU_LOCK.read_text().strip())
                if self._is_process_alive(pid):
                    return False
            except:
                pass
            GPU_LOCK.unlink(missing_ok=True)
        
        # 检查 GPU 进程
        result = subprocess.run(
            "pgrep -f 'ffmpeg|python.*promo_api|python.*sd'",
            shell=True, capture_output=True
        )
        return result.returncode != 0
    
    def _is_process_alive(self, pid):
        try:
            import os
            os.kill(pid, 0)
            return True
        except:
            return False
    
    def acquire_lock(self):
        """获取 GPU 锁"""
        GPU_LOCK.write_text(str(os.getpid()))
    
    def release_lock(self):
        """释放 GPU 锁"""
        GPU_LOCK.unlink(missing_ok=True)
    
    def submit_task(self, task_name, task_cmd, priority=5):
        """提交 GPU 任务"""
        task = {
            "name": task_name,
            "cmd": task_cmd,
            "priority": priority,
            "submitted": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # 保存到任务队列
        queue_file = TASKS_DIR / f"gpu_queue_{int(time.time())}.json"
        with open(queue_file, 'w') as f:
            json.dump(task, f)
        
        print(f"[GPU] 任务已提交: {task_name}")
        return queue_file
    
    def process_queue(self):
        """处理 GPU 任务队列"""
        while True:
            # 等待 GPU 空闲
            while not self.is_gpu_idle():
                time.sleep(5)
            
            # 获取待处理任务
            queue_files = sorted(TASKS_DIR.glob("gpu_queue_*.json"),
                                key=lambda x: x.stat().st_mtime)
            
            if not queue_files:
                time.sleep(10)
                continue
            
            # 执行任务
            for qf in queue_files:
                with open(qf, 'r') as f:
                    task = json.load(f)
                
                if not self.is_gpu_idle():
                    break
                
                self.acquire_lock()
                self.current_task = task['name']
                print(f"[GPU] 执行: {task['name']}")
                
                result = subprocess.run(task['cmd'], shell=True)
                
                self.release_lock()
                self.current_task = None
                
                # 标记完成
                task['status'] = "done" if result.returncode == 0 else "failed"
                task['completed'] = datetime.now().isoformat()
                
                done_file = TASKS_DIR / f"gpu_done_{qf.stem}.json"
                with open(done_file, 'w') as f:
                    json.dump(task, f)
                
                qf.unlink()
                
                print(f"[GPU] 完成: {task['name']} (success={result.returncode==0})")
            
            time.sleep(5)
    
    def start(self):
        """启动 GPU 管理器"""
        self.running = True
        print("[GPU] 资源管理器启动")
        
        # 启动队列处理线程
        thread = threading.Thread(target=self.process_queue, daemon=True)
        thread.start()
        
        return thread

if __name__ == "__main__":
    import os
    manager = GPUManager()
    
    # 示例：提交临时任务
    if len(sys.argv) > 1:
        task_name = sys.argv[1]
        task_cmd = sys.argv[2] if len(sys.argv) > 2 else ""
        manager.submit_task(task_name, task_cmd)
    else:
        manager.start()
        # 保持运行
        while True:
            time.sleep(60)
