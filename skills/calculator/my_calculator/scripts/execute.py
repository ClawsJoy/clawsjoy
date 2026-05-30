#!/usr/bin/env python3
"""计算器执行脚本"""

def execute(expression: str) -> dict:
    """执行计算"""
    try:
        result = eval(expression)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(execute(sys.argv[1]))
