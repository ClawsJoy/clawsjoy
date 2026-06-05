#!/usr/bin/env python3
"""自动集成优化到 agent_gateway_enhanced.py"""

import re

file_path = "agent_gateway_enhanced.py"

with open(file_path, "r") as f:
    content = f.read()

# 1. 检查是否已导入优化模块
if "from core.lib.response_cache import response_cache" not in content:
    # 在导入区域添加
    content = content.replace(
        "from core.lib.smart_active_service import smart_service",
        "from core.lib.smart_active_service import smart_service\n\n# 性能优化模块\nfrom core.lib.response_cache import response_cache\nfrom core.lib.performance_middleware import monitor_performance, get_perf_stats\nfrom core.lib.rate_limiter import rate_limit, rate_limiter",
    )
    print("✅ 添加导入语句")

# 2. 查找 enhanced_chat 函数并添加装饰器和缓存
# 匹配 enhanced_chat 函数定义
pattern = (
    r'(@app\.route\([\'"]/api/v5/enhanced/chat[\'"],.*?\)\s*)(def enhanced_chat\(\):)'
)


def replace_func(match):
    route_decorator = match.group(1)
    func_def = match.group(2)
    return f"{route_decorator}\n@monitor_performance\n@rate_limit(limit=30, window=60)\n{func_def}"


if re.search(pattern, content):
    content = re.sub(pattern, replace_func, content)
    print("✅ 添加装饰器")
else:
    print("⚠️ 未找到 enhanced_chat 函数，请手动检查")

# 3. 在 enhanced_chat 函数内部添加缓存逻辑
# 查找函数体开始位置
cache_pattern = r"(def enhanced_chat\(\):.*?)(\s+data = request\.get_json)"


def add_cache_logic(match):
    before = match.group(1)
    after = match.group(2)

    cache_logic = """    
    # 尝试从缓存获取
    cached = response_cache.get(user_id, message)
    if cached:
        return jsonify({
            "success": True,
            "response": cached,
            "cached": True,
            "user_id": user_id
        })"""

    return before + cache_logic + after


if re.search(cache_pattern, content, re.DOTALL):
    content = re.sub(cache_pattern, add_cache_logic, content, flags=re.DOTALL)
    print("✅ 添加缓存读取逻辑")
else:
    print("⚠️ 添加缓存逻辑失败，请手动添加")

# 4. 在返回前添加缓存存储逻辑
# 查找返回语句前的位置
return_pattern = r"(return jsonify\({.*?}\)\s*)(?=\n|$)"
# 这个比较复杂，手动提示

with open(file_path, "w") as f:
    f.write(content)

print("\n" + "=" * 50)
print("⚠️ 请手动完成以下步骤：")
print("=" * 50)
print("1. 在 enhanced_chat 函数中，找到返回结果的地方")
print("2. 在 return 之前添加：")
print(
    """   # 缓存结果
   response_cache.set(user_id, message, result)"""
)
print("3. 确保 result 变量包含实际响应内容")
