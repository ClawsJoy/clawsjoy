#!/usr/bin/env python3
"""主动跑主循环 v1.0.0 - 系统永不停止"""

import sys
import time
import signal
sys.path.insert(0, "/mnt/d/clawsjoy_clean")

from lib.task_queue import task_queue
from lib.task_generator import task_generator
from lib.skill_loader_v3 import skill_loader

running = True

def signal_handler(sig, frame):
    global running
    print("\n🛑 停止主动跑引擎...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print("=" * 50)
    print("🤖 ClawsJoy 主动跑引擎 v1.0.0")
    print("=" * 50)
    print("系统将自主产生任务、执行任务、持续运行\n")
    
    cycle = 0
    while running:
        cycle += 1
        
        # 生成新任务
        generated = task_generator.generate()
        
        # 获取下一个任务
        task = task_queue.pop_next()
        
        if task:
            print(f"[{cycle}] 执行: {task.name} ({task.priority.name})")
            task_queue.start(task)
            
            try:
                result = skill_loader.execute(task.skill, task.params)
                if result.get("success"):
                    task_queue.complete(task, result)
                    print(f"  ✅ 完成")
                else:
                    task_queue.fail(task, result.get("error", "unknown"))
                    print(f"  ❌ 失败，重试 {task.retry_count}/{task.max_retry}")
            except Exception as e:
                task_queue.fail(task, str(e))
                print(f"  ❌ 异常: {e}")
        else:
            if cycle % 10 == 0:
                status = task_queue.get_status()
                print(f"[{cycle}] 空闲中 | 队列:{status['pending']} | 完成:{status['completed']}")
        
        time.sleep(5)
    
    print("\n✅ 主动跑引擎停止")

if __name__ == "__main__":
    main()
