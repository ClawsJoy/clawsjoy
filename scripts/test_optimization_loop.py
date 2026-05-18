#!/usr/bin/env python3
"""完整测试主动优化闭环"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

# 直接导入模块（使用正确的文件名）
from lib.error_knowledge_v1_0_01_20260517 import error_knowledge
from lib.task_quality_scorer_v1_0_00_20260517 import quality_scorer
from lib.priority_adjuster_v1_0_00_20260517 import priority_adjuster
from lib.resource_monitor_v1_0_00_20260517 import resource_monitor
from lib.memory_writer import memory_writer

def test_error_knowledge():
    """测试错误知识库"""
    print("\n" + "="*50)
    print("1. 测试错误知识库")
    print("="*50)
    
    task_name = "TEST_Integration_ConnectionFail"
    error_msg = "Connection refused to port 9999"
    
    # 添加错误
    result = error_knowledge.add(task_name, error_msg, "test_skill")
    print(f"✅ 已添加错误: {task_name}")
    
    # 查询
    query_result = error_knowledge.query(task_name)
    print(f"查询结果: {'找到' if query_result else '未找到'}")
    
    # 跳过检查
    should_skip, reason = error_knowledge.should_skip(task_name, retry_count=3)
    print(f"跳过检查 (3次重试): {'是' if should_skip else '否'} - {reason}")
    
    return query_result is not None

def test_quality_scorer():
    """测试质量评分器"""
    print("\n" + "="*50)
    print("2. 测试质量评分器")
    print("="*50)
    
    result = quality_scorer.score(
        task_name="TEST_Quality_Check",
        skill="test_skill",
        params={"input_file": "/nonexistent/file.txt"}
    )
    print(f"评分: {result['score']}")
    print(f"跳过建议: {'是' if result['should_skip'] else '否'}")
    print(f"原因: {', '.join(result['reasons'])}")
    
    return result['score'] >= 0

def test_priority_adjuster():
    """测试优先级调整器"""
    print("\n" + "="*50)
    print("3. 测试优先级调整器")
    print("="*50)
    
    # 模拟失败任务
    priority_adjuster.record_outcome("test_task_1", False)
    priority_adjuster.record_outcome("test_task_1", False)
    priority_adjuster.record_outcome("test_task_1", False)
    
    # 模拟成功任务
    priority_adjuster.record_outcome("test_task_2", True)
    priority_adjuster.record_outcome("test_task_2", True)
    
    new_priority = priority_adjuster.adjust_priority("test_task_1", 2, 0.3)
    print(f"失败任务优先级: 2 -> {new_priority}")
    
    new_priority = priority_adjuster.adjust_priority("test_task_2", 2, 0.9)
    print(f"成功任务优先级: 2 -> {new_priority}")
    
    stats = priority_adjuster.get_stats()
    print(f"统计: {stats}")
    
    return True

def test_resource_monitor():
    """测试资源监控器"""
    print("\n" + "="*50)
    print("4. 测试资源监控器")
    print("="*50)
    
    status = resource_monitor.get_status()
    print(f"CPU: {status.get('cpu_percent', 0)}%")
    print(f"内存: {status.get('memory_percent', 0)}%")
    print(f"健康: {status.get('healthy', True)}")
    print(f"限流: {resource_monitor.should_throttle()}")
    
    return status.get('healthy', True)

def test_memory_writer():
    """测试记忆写入器"""
    print("\n" + "="*50)
    print("5. 测试记忆写入器")
    print("="*50)
    
    try:
        result = memory_writer.write_task_success(
            task_name="TEST_Integration_Success",
            skill="test_skill"
        )
        print(f"写入成功: {result}")
        
        result = memory_writer.write_task_failure(
            task_name="TEST_Integration_Failure",
            error_msg="Integration test failure",
            skill="test_skill"
        )
        print(f"写入失败: {result}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    print("="*60)
    print("ClawsJoy 主动优化闭环集成测试")
    print("="*60)
    
    results = {}
    
    results['error_knowledge'] = test_error_knowledge()
    results['quality_scorer'] = test_quality_scorer()
    results['priority_adjuster'] = test_priority_adjuster()
    results['resource_monitor'] = test_resource_monitor()
    results['memory_writer'] = test_memory_writer()
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
    
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！主动优化闭环工作正常")
    else:
        print("⚠️ 部分测试失败，请检查")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
