import re
import os

# 替换硬编码密钥
file_path = 'core/lib/auth_api.py'
with open(file_path, 'r') as f:
    content = f.read()

content = re.sub(
    r'JWT_SECRET = "clawsjoy-production-secret-key-2024"',
    'JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")',
    content
)

with open(file_path, 'w') as f:
    f.write(content)
    
print("✅ JWT 密钥已移至环境变量")
