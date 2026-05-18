#!/usr/bin/env python3
"""主动跑主循环 v3.0.02 - 配置驱动版"""

import sys
import time
import signal
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.config_driver import config_driver
from lib.smart_config import smart_config
from lib.task_queue import task_queue
from lib.task_generator import task_generator
from lib.skill_loader_v3 import skill_loader
from lib.error_knowledge import error_knowledge
from lib.task_quality_scorer import quality_scorer
from lib.priority_adjuster import priority_adjuster
from lib.resource_monitor import resource_monitor

running = True

def signal_handler(sig, frame):
    global running
    print("\n🛑 停止主动跑引擎...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def should_skip_task(task) -> tuple:
    """判断是否应该跳过任务（配置驱动）"""
    
    # 1. 资源限流检查
    if resource_monitor.should_throttle():
        cooldown = resource_monitor.get_cooldown_remaining()
        return True, f"系统负载过高，冷却 {cooldown}s"
    
    # 2. 质量预评分
    if config_driver.get('optimization.enable_quality_scoring', True):
        score_result = quality_scorer.score(
            task_name=task.name,
            skill=task.skill,
            params=task.params
        )
        
        if score_result.get('should_skip'):
            return True, f"质量评分过低 ({score_result['score']}): {', '.join(score_result['reasons'])}"
    
    # 3. 错误知识查询
    if config_driver.get('optimization.enable_error_knowledge', True):
        should_skip, reason = error_knowledge.should_skip(task.name)
        if should_skip:
            return True, reason
    
    return False, ""


def main():
    # 读取配置
    generation_interval = config_driver.get('tasks.generation_interval', 5)
    max_concurrent = config_driver.get('tasks.max_concurrent', 5)
    queue_persist = config_driver.get('tasks.queue_persist', True)
    
    print("=" * 50)
    print("🤖 ClawsJoy 主动跑引擎 v3.0.02 (配置驱动版)")
    print("=" * 50)
    print(f"配置驱动: v{config_driver.VERSION}")
    print(f"质量评分: {'启用' if config_driver.get('optimization.enable_quality_scoring') else '禁用'}")
    print(f"错误知识: {'启用' if config_driver.get('optimization.enable_error_knowledge') else '禁用'}")
    print(f"优先级调整: {'启用' if config_driver.get('optimization.enable_priority_adjust') else '禁用'}")
    print(f"资源限流: {'启用' if config_driver.get('optimization.enable_resource_throttle') else '禁用'}")
    print("")
    
    cycle = 0
    skipped_count = 0
    success_count = 0
    fail_count = 0
    
    while running:
        cycle += 1
        
        # 生成新任务
        generated = task_generator.generate()
        
        # 获取下一个任务
        task = task_queue.pop_next()
        
        if task:
            # 主动优化：判断是否跳过
            skip, skip_reason = should_skip_task(task)
            
            if skip:
                print(f"[{cycle}] ⏭️ 跳过: {task.name} ({skip_reason})")
                skipped_count += 1
                continue
            
            # 调整优先级
            new_priority = priority_adjuster.adjust_priority(
                task.name, 
                task.priority.value if hasattr(task.priority, 'value') else 2
            )
            if new_priority != (task.priority.value if hasattr(task.priority, 'value') else 2):
                print(f"[{cycle}] 📊 优先级调整: {task.name} -> {new_priority}")
            
            print(f"[{cycle}] 执行: {task.name}")
            task_queue.start(task)
            
            try:
                result = skill_loader.execute(task.skill, task.params)
                
                if result.get("success"):
                    task_queue.complete(task, result)
                    print(f"  ✅ 完成")
                    success_count += 1
                    priority_adjuster.record_outcome(task.name, True)
                else:
                    error_msg = result.get("error", "unknown")
                    task_queue.fail(task, error_msg)
                    print(f"  ❌ 失败: {error_msg[:100]}")
                    fail_count += 1
                    priority_adjuster.record_outcome(task.name, False)
                    
                    # 学习失败
                    if config_driver.get('optimization.auto_learn_failures', True):
                        error_knowledge.add(task.name, error_msg, task.skill)
                    
            except Exception as e:
                error_msg = str(e)
                task_queue.fail(task, error_msg)
                print(f"  ❌ 异常: {error_msg[:100]}")
                fail_count += 1
                priority_adjuster.record_outcome(task.name, False)
                
                if config_driver.get('optimization.auto_learn_failures', True):
                    error_knowledge.add(task.name, error_msg, task.skill)
        else:
            if cycle % 10 == 0:
                status = task_queue.get_status()
                total = success_count + fail_count + skipped_count
                rate = (success_count / max(total, 1)) * 100
                print(f"[{cycle}] 空闲 | 队列:{status.get('pending', 0)} | "
                      f"成功:{success_count} 失败:{fail_count} 跳过:{skipped_count} "
                      f"成功率:{rate:.1f}%")
        
        time.sleep(generation_interval)
    
    # 最终统计
    print("\n" + "=" * 50)
    print("📊 主动跑引擎停止")
    total = success_count + fail_count + skipped_count
    rate = (success_count / max(total, 1)) * 100
    print(f"   成功: {success_count}")
    print(f"   失败: {fail_count}")
    print(f"   跳过: {skipped_count}")
    print(f"   成功率: {rate:.1f}%")
    print("=" * 50)


if __name__ == "__main__":
    main()
