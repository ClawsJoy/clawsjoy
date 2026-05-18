#!/usr/bin/env python3
"""主动跑主循环 v3.0.01 - 主动优化版"""

import sys
import time
import signal
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.smart_config import smart_config
from lib.task_queue import task_queue
from lib.task_generator import task_generator
from lib.skill_loader_v3 import skill_loader
from lib.error_knowledge_v1_0_00_20260517 import error_knowledge
from lib.task_quality_scorer_v1_0_00_20260517 import quality_scorer
from lib.memory_writer_v1_0_01_20260517 import memory_writer

running = True

def signal_handler(sig, frame):
    global running
    print("\n🛑 停止主动跑引擎...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def should_skip_task(task) -> tuple:
    """判断是否应该跳过任务"""
    
    # 1. 质量预评分
    score_result = quality_scorer.score(
        task_name=task.name,
        skill=task.skill,
        params=task.params
    )
    
    if score_result['should_skip']:
        return True, f"质量评分过低 ({score_result['score']}): {', '.join(score_result['reasons'])}"
    
    # 2. 错误知识查询
    error = error_knowledge.query(task.name)
    if error:
        retry_count = error.get('retry_count', 0)
        if retry_count >= error_knowledge.max_retry_same_error:
            return True, f"重复失败 {retry_count} 次，建议: {error.get('solution', '人工介入')}"
    
    return False, ""


def main():
    print("=" * 50)
    print("🤖 ClawsJoy 主动跑引擎 v3.0.01 (主动优化版)")
    print("=" * 50)
    print("特性: 质量预评分 | 错误知识查询 | 失败学习")
    print("")
    
    # 显示统计
    error_stats = error_knowledge.get_stats()
    print(f"📚 错误知识库: {error_stats['total_errors']} 条")
    print(f"⭐ 质量阈值: {quality_scorer.min_score_to_execute}")
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
                
                # 记录跳过
                memory_writer.write_task_outcome(
                    task_name=task.name,
                    status="skipped",
                    skill=task.skill,
                    error_msg=skip_reason
                )
                continue
            
            print(f"[{cycle}] 执行: {task.name} ({task.priority.name})")
            task_queue.start(task)
            
            try:
                result = skill_loader.execute(task.skill, task.params)
                
                if result.get("success"):
                    task_queue.complete(task, result)
                    print(f"  ✅ 完成")
                    success_count += 1
                    
                    # 写入成功记忆
                    memory_writer.write_task_success(
                        task_name=task.name,
                        skill=task.skill
                    )
                else:
                    error_msg = result.get("error", "unknown")
                    task_queue.fail(task, error_msg)
                    print(f"  ❌ 失败: {error_msg[:100]}")
                    fail_count += 1
                    
                    # 写入失败记忆并学习
                    memory_writer.write_task_failure(
                        task_name=task.name,
                        error_msg=error_msg,
                        skill=task.skill
                    )
                    
                    # 主动优化：学习失败
                    error_knowledge.add(
                        task_name=task.name,
                        error_msg=error_msg,
                        skill=task.skill
                    )
                    
            except Exception as e:
                error_msg = str(e)
                task_queue.fail(task, error_msg)
                print(f"  ❌ 异常: {error_msg[:100]}")
                fail_count += 1
                
                # 学习异常
                error_knowledge.add(
                    task_name=task.name,
                    error_msg=error_msg,
                    skill=task.skill
                )
        else:
            if cycle % 10 == 0:
                status = task_queue.get_status()
                total = success_count + fail_count + skipped_count
                rate = (success_count / max(total, 1)) * 100
                print(f"[{cycle}] 空闲 | 队列:{status['pending']} | "
                      f"成功:{success_count} 失败:{fail_count} 跳过:{skipped_count} "
                      f"成功率:{rate:.1f}%")
        
        time.sleep(5)
    
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
