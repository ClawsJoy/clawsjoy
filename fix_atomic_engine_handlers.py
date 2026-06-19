import re

file_path = "engine/atomic/atomic_engine_v25.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在所有 handler 的 return 之前添加 _ensure_v25_response 包装
# 方案：修改 process 方法，在 _route 返回后统一包装

# 找到 process 方法中的 result = self._route(request, action)
# 在之后添加包装逻辑

pattern = r'(result = self\._route\(request, action\))(.*?)(if isinstance\(result, dict\):)'

def add_wrapper(match):
    route_line = match.group(1)
    middle = match.group(2)
    if_line = match.group(3)
    
    # 在 middle 中插入包装逻辑
    wrapper = '''
        # 🔧 确保所有 handler 返回的结果都经过 2.5 层 JSON 包装
        if isinstance(result, dict) and "version" not in result:
            # 提取响应内容
            content = result.get("response", result.get("output_content", "处理完成"))
            # 提取 output_data（安全地）
            output_data = {}
            for key in ["agent", "intent", "memories_used", "success", "result", "error"]:
                if key in result:
                    output_data[key] = result[key]
            result = self._create_response(
                request,
                content,
                "completed" if result.get("success", True) else "failed",
                output_data
            )
'''
    
    return route_line + wrapper + '\n' + if_line

content = re.sub(pattern, add_wrapper, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ atomic_engine_v25.py 已修复 - 所有 handler 都经过 2.5 层 JSON 包装")
