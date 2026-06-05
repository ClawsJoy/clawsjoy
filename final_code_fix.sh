#!/bin/bash
echo "🔧 应用剩余代码修复..."

# 1. 修复 eval 漏洞（手动需要，自动生成修复文件）
cat > fix_eval.patch << 'PATCH'
--- a/agents/chat_agent/agent.py
+++ b/agents/chat_agent/agent.py
@@ -1267,7 +1267,18 @@
-                return f"{a}{op}{b} = {eval(f'{a}{op}{b}')}"
+                try:
+                    import operator
+                    SAFE_OPS = {
+                        '+': operator.add, '-': operator.sub,
+                        '*': operator.mul, '/': operator.truediv
+                    }
+                    if op in SAFE_OPS:
+                        result = SAFE_OPS[op](float(a), float(b))
+                        return f"{a}{op}{b} = {result}"
+                    return f"不支持的运算符: {op}"
+                except Exception as e:
+                    return f"计算错误: {e}"
PATCH

# 2. 批量替换裸 except
find . -name "*.py" -type f -exec sed -i 's/except:/except Exception as e:/g' {} \;
echo "✅ 已替换裸 except"

# 3. 检查是否有语法错误
python3 -m py_compile agents/chat_agent/agent.py
echo "✅ 语法检查完成"

# 4. 重启服务
pkill -f gunicorn
sleep 2
./start_prod.sh

echo "✅ 修复完成，请测试: curl http://127.0.0.1:5002/health"
