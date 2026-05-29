import yaml
import re
from pathlib import Path

# 读取 routes.yaml
with open('config/routes/routes.yaml', 'r') as f:
    routes = yaml.safe_load(f)

# 获取所有需要的处理器
required_handlers = set()
for route in routes.get('routes', []):
    if route.get('enabled', True):
        required_handlers.add(route['handler'])

# 读取 route_handlers.py 中已注册的处理器
with open('lib/route_handlers.py', 'r') as f:
    content = f.read()

registered_handlers = set(re.findall(r'@register\("([^"]+)"\)', content))

missing = required_handlers - registered_handlers
print(f"路由总数: {len(required_handlers)}")
print(f"已注册处理器: {len(registered_handlers)}")
print(f"缺失处理器数量: {len(missing)}")
if missing:
    print("\n缺失的处理器:")
    for h in sorted(missing):
        print(f"  ⚠️ {h}")
else:
    print("\n✅ 所有路由处理器都已注册！")
