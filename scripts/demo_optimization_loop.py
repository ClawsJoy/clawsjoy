#!/usr/bin/env python3
"""演示主动优化闭环 - 完整流程"""

import sys
import time
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.error_knowledge import error_knowledge
from lib.task_quality_scorer import quality_scorer
from lib.priority_adjuster import priority_adjuster
from lib.resource_monitor import resource_monitor
from lib.task_queue import task_queue, Priority, Task
import uuid

def demo_error_learning():
    """演示错误学习和跳过机制"""
    print("\n" + "="*60)
    print("演示1: 错误学习与主动跳过")
    print("="*60)
    
    task_name = "DEMO_FailTask_" + str(uuid.uuid4())[:6]
    
    print(f"\n任务: {task_name}")
    
    # 第1次：执行失败
    print("\n第1次执行: 失败")
    error_knowledge.add(task_name, "Connection refused to port 9999", "demo_skill")
    
    # 第2次：执行失败
    print("第2次执行: 失败")
    error_knowledge.add(task_name, "Connection refused to port 9999", "demo_skill")
    
    # 第3次：执行失败
    print("第3次执行: 失败")
    error_knowledge.add(task_name, "Connection refused to port 9999", "demo_skill")
    
    # 第4次：应该被跳过
    print("\n第4次执行前检查:")
    should_skip, reason = error_knowledge.should_skip(task_name)
    print(f"  是否跳过: {should_skip}")
    print(f"  原因: {reason}")
    
    # 查看错误统计
    error_info = error_knowledge.query(task_name)
    print(f"\n错误统计: 重试次数 = {error_info.get('retry_count', 0)}")

def demo_quality_scoring():
    """演示质量预评分"""
    print("\n" + "="*60)
    print("演示2: 质量预评分")
    print("="*60)
    
    test_cases = [
        ("高质量任务", "manju_maker", {}),
        ("低质量任务 - 测试", "test_skill", {"input_file": "/nonexistent/file.txt"}),
    ]
    
    for name, skill, params in test_cases:
        result = quality_scorer.score(name, skill, params)
        print(f"\n任务: {name}")
        print(f"  评分: {result['score']}")
        print(f"  建议跳过: {result['should_skip']}")
        if result['reasons']:
            print(f"  原因: {', '.join(result['reasons'])}")

def demo_priority_adjustment():
    """演示优先级动态调整"""
    print("\n" + "="*60)
    print("演示3: 优先级动态调整")
    print("="*60)
    
    # 模拟任务历史
    priority_adjuster.record_outcome("high_success_task", True)
    priority_adjuster.record_outcome("high_success_task", True)
    priority_adjuster.record_outcome("high_success_task", True)
    
    priority_adjuster.record_outcome("high_fail_task", False)
    priority_adjuster.record_outcome("high_fail_task", False)
    priority_adjuster.record_outcome("high_fail_task", False)
    
    # 调整优先级
    new_priority_high = priority_adjuster.adjust_priority("high_success_task", 2, 0.9)
    new_priority_low = priority_adjuster.adjust_priority("high_fail_task", 2, 0.1)
    
    print(f"\n高成功率任务: 优先级 2 -> {new_priority_high}")
    print(f"高失败率任务: 优先级 2 -> {new_priority_low}")
    
    print(f"\n统计: {priority_adjuster.get_stats()}")

def demo_resource_monitoring():
    """演示资源监控"""
    print("\n" + "="*60)
    print("演示4: 资源监控")
    print("="*60)
    
    status = resource_monitor.get_status()
    print(f"\nCPU: {status.get('cpu_percent', 0)}%")
    print(f"内存: {status.get('memory_percent', 0)}%")
    print(f"磁盘: {status.get('disk_percent', 0)}%")
    print(f"系统健康: {status.get('healthy', True)}")
    print(f"建议限流: {resource_monitor.should_throttle()}")

def demo_integration():
    """演示完整闭环"""
    print("\n" + "="*60)
    print("演示5: 完整主动优化闭环")
    print("="*60)
    
    task_name = "DEMO_Integration_" + str(uuid.uuid4())[:6]
    print(f"\n任务: {task_name}")
    
    # 步骤1: 质量预评分
    print("\n步骤1 - 质量预评分:")
    score_result = quality_scorer.score(task_name, "demo_skill", {})
    print(f"  评分: {score_result['score']}")
    
    if score_result['should_skip']:
        print(f"  ⏭️ 任务被跳过: {score_result['reasons']}")
        return
    
    # 步骤2: 检查错误历史
    print("\n步骤2 - 检查错误历史:")
    error = error_knowledge.query(task_name)
    if error:
        print(f"  ⚠️ 发现历史错误: {error.get('error', '')[:50]}")
        if error.get('retry_count', 0) >= 3:
            print(f"  ⏭️ 任务被跳过 (重复失败 {error.get('retry_count')} 次)")
            return
    else:
        print(f"  ✅ 无历史错误")
    
    # 步骤3: 检查资源
    print("\n步骤3 - 检查系统资源:")
    if resource_monitor.should_throttle():
        print(f"  ⏸️ 系统负载过高，延迟执行")
    else:
        print(f"  ✅ 资源充足")
    
    # 步骤4: 模拟执行
    print("\n步骤4 - 执行任务:")
    print(f"  ✅ 任务执行成功")
    
    # 步骤5: 记录结果
    print("\n步骤5 - 记录结果:")
    priority_adjuster.record_outcome(task_name, True)
    print(f"  ✅ 已记录到优先级调整器")
    
    print("\n" + "="*60)
    print("🎉 主动优化闭环演示完成")
    print("="*60)

def main():
    print("="*60)
    print("ClawsJoy 主动优化闭环 - 完整演示")
    print("="*60)
    
    demo_error_learning()
    demo_quality_scoring()
    demo_priority_adjustment()
    demo_resource_monitoring()
    demo_integration()
    
    print("\n" + "="*60)
    print("📊 闭环总结")
    print("="*60)
    print("""
    主动优化闭环包含:
    
    1. 质量预评分 ──→ 低质量任务被提前过滤
    2. 错误知识查询 ──→ 重复失败被自动跳过  
    3. 优先级调整 ──→ 高成功率任务获得更高优先级
    4. 资源监控 ──→ 系统负载高时自动限流
    5. 失败学习 ──→ 新错误自动加入知识库
    
    所有模块版本化、配置驱动、可追溯。
    """)

if __name__ == "__main__":
    main()
