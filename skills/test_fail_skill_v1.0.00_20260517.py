"""测试失败技能 - 用于验证错误学习"""

def execute(params):
    """总是返回失败"""
    task_name = params.get('task_name', 'unknown')
    
    # 模拟不同类型的失败
    fail_type = params.get('fail_type', 'connection')
    
    if fail_type == 'connection':
        return {
            "success": False,
            "error": f"Connection refused to port 9999 for task: {task_name}"
        }
    elif fail_type == 'not_found':
        return {
            "success": False,
            "error": f"No video found for task: {task_name}"
        }
    elif fail_type == 'timeout':
        return {
            "success": False,
            "error": f"Timeout after 30 seconds for task: {task_name}"
        }
    else:
        return {
            "success": False,
            "error": f"Unknown error for task: {task_name}"
        }

# 技能元数据
skill_info = {
    "name": "test_fail_skill",
    "version": "1.0.00",
    "description": "测试失败技能，用于验证错误学习",
    "author": "ClawsJoy",
    "tags": ["test", "debug"]
}
