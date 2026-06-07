""" - """


class CalculatorSkill:
    name = "calculator"
    description = "基本计算器"
    version = "2.0.0"

    def execute(self, params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        op = params.get("op", "+")
        expression = params.get("expression", "")

        # 支持表达式计算
        if expression:
            try:
                # 安全的表达式计算
                result = eval(expression, {"__builtins__": {}}, {})
                return {"success": True, "result": result, "expression": expression}
            except Exception as e:
                return {"success": False, "error": f"表达式错误: {e}"}

        # 基础运算
        try:
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            elif op == "*":
                result = a * b
            elif op == "/":
                result = a / b if b != 0 else "除数不能为零"
            else:
                return {"success": False, "error": f"不支持的操作: {op}"}

            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
