import re

with open('promo_api.py', 'r') as f:
    content = f.read()

# 找到 make_video 调用并添加时长参数
# 匹配模式: make_video 'title' 'image_dir' 'output' 'name'
pattern = r"(make_video\s+['\"][^'\"]+['\"]\s+['\"][^'\"]+['\"]\s+['\"][^'\"]+['\"]\s+['\"][^'\"]+['\"])"
replacement = r"\1 '15'"

content = re.sub(pattern, replacement, content)

with open('promo_api.py', 'w') as f:
    f.write(content)

print("✅ 已添加时长参数")
