"""计算器技能 - 执行数学运算"""

description = "计算 加法 减法 乘法 除法 数学运算 算术 算数 计算器 数值计算 公式计算"

def execute(params):
    """执行计算"""
    expression = params.get('expression', '')
    if not expression:
        return {"error": "缺少表达式"}
    
    try:
        # 安全计算
        result = eval(expression, {"__builtins__": {}}, {})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
