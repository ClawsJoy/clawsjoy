"""数学计算执行器"""

import re
from core.lib.unified_config import unified_config


class MathExecutor:
    """数学计算执行器"""
    
    name = "math_executor"
    
    def execute(self, goal: str, params: dict = None) -> dict:
        """执行数学计算"""
        pattern = unified_config.get("brain_rules.math.pattern", r'(\d+)\s*([+\-*/xX])\s*(\d+)')
        match = re.search(pattern, goal.replace('？', '').replace('?', ''))
        if not match:
            return {"success": False, "error": "无法解析数学表达式"}

        a, op, b = int(match.group(1)), match.group(2), int(match.group(3))

        # 统一运算符
        if op == 'x' or op == 'X':
            op = '*'

        operations = {
            '+': lambda: a + b,
            '-': lambda: a - b,
            '*': lambda: a * b,
            '/': lambda: a / b if b != 0 else None
        }

        if op in operations:
            result = operations[op]()
            if result is None:
                return {"success": False, "error": "除数不能为0"}
            return {
                "success": True,
                "result": result,
                "expression": f"{a} {op} {b} = {result}"
            }

        return {"success": False, "error": f"不支持的运算符: {op}"}


math_executor = MathExecutor()
