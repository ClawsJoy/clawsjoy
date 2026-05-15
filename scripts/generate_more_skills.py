"""批量生成更多基础技能"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from pathlib import Path

def generate_skill(name, description, category, code_template):
    skill_content = f'''"""
{description}
"""
class {name.capitalize()}Skill:
    name = "{name}"
    description = "{description}"
    version = "1.0.0"
    category = "{category}"
    
    def execute(self, params):
        {code_template}
        return {{"success": True, "result": result}}

skill = {name.capitalize()}Skill()
'''
    skill_path = Path(f"skills/{category}/{name}.py")
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(skill_content, encoding='utf-8')
    print(f"  ✅ 生成技能: {category}/{name}.py")

# 日期时间技能
datetime_skills = [
    ("get_time", "获取当前时间", "from datetime import datetime; result = datetime.now().isoformat()"),
    ("format_date", "格式化日期", "from datetime import datetime; date = params.get('date'); format = params.get('format', '%Y-%m-%d'); result = datetime.strptime(date, '%Y-%m-%d').strftime(format) if date else datetime.now().strftime(format)"),
    ("date_diff", "计算日期差", "from datetime import datetime; d1 = params.get('date1'); d2 = params.get('date2'); result = (datetime.strptime(d2, '%Y-%m-%d') - datetime.strptime(d1, '%Y-%m-%d')).days"),
]

# 文件操作技能
file_skills = [
    ("read_file", "读取文件", "from pathlib import Path; path = params.get('path'); result = Path(path).read_text() if Path(path).exists() else None"),
    ("write_file", "写入文件", "from pathlib import Path; path = params.get('path'); content = params.get('content', ''); Path(path).write_text(content); result = f'写入成功: {path}'"),
    ("list_files", "列出文件", "from pathlib import Path; directory = params.get('directory', '.'); result = [str(f) for f in Path(directory).iterdir() if f.is_file()]"),
    ("file_exists", "检查文件存在", "from pathlib import Path; path = params.get('path'); result = Path(path).exists()"),
]

# 网络请求技能
http_skills = [
    ("http_get", "HTTP GET请求", "import requests; url = params.get('url'); response = requests.get(url, timeout=30); result = response.text"),
    ("http_post", "HTTP POST请求", "import requests; url = params.get('url'); data = params.get('data', {}); response = requests.post(url, json=data, timeout=30); result = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text"),
    ("download_file", "下载文件", "import requests; url = params.get('url'); path = params.get('path'); response = requests.get(url, timeout=60); Path(path).write_bytes(response.content); result = f'下载完成: {path}'"),
]

# 加密技能
crypto_skills = [
    ("md5_hash", "MD5哈希", "import hashlib; text = params.get('text', ''); result = hashlib.md5(text.encode()).hexdigest()"),
    ("base64_encode", "Base64编码", "import base64; text = params.get('text', ''); result = base64.b64encode(text.encode()).decode()"),
    ("base64_decode", "Base64解码", "import base64; data = params.get('data', ''); result = base64.b64decode(data).decode()"),
]

# 生成所有技能
print("生成日期时间技能...")
for name, desc, code in datetime_skills:
    generate_skill(name, desc, "tools", code)

print("生成文件操作技能...")
for name, desc, code in file_skills:
    generate_skill(name, desc, "tools", code)

print("生成网络请求技能...")
for name, desc, code in http_skills:
    generate_skill(name, desc, "network", code)

print("生成加密技能...")
for name, desc, code in crypto_skills:
    generate_skill(name, desc, "tools", code)

print("\n✅ 第二批技能生成完成")
