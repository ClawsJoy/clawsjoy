#!/usr/bin/env python3
"""my_calculator 技能执行脚本"""

def execute(params):
a = params.get('a', 0)
b = params.get('b', 0)
op = params.get('op', 'add')

if op == 'add':
result = a + b
elif op == 'sub':
result = a - b
elif op == 'mul':
result = a * b
elif op == 'div':
result = a / b if b != 0 else 'error'
else:
result = a + b

return {"result": result, "skill": "my_calculator"}

def get_help():
return "计算器指令格式：a=数字 b=数字 op=add/sub/mul/div"

if name == "main":
print(execute({"a": 10, "b": 5, "op": "add"}))
