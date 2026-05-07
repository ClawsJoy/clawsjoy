#!/usr/bin/env python3
"""命令行 OAuth 认证 - 不需要本地服务器"""

import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtubepartner"
]

CLIENT_SECRET = Path("/mnt/d/clawsjoy/config/youtube/client_secrets.json")
TOKEN_FILE = Path("/mnt/d/clawsjoy/config/youtube/token.pickle")

print("🔐 YouTube OAuth 认证")
print("=" * 50)

flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)

# 使用 authorization_code 模式（手动复制链接）
auth_url, _ = flow.authorization_url(prompt='consent')
print("\n📋 请复制以下链接到浏览器打开：")
print("=" * 50)
print(auth_url)
print("=" * 50)
print("\n👉 在浏览器中登录并授权后，地址栏会显示：")
print("   http://localhost/?code=4/xxxxxxxxxxx")
print("\n👉 复制 code= 后面的那一串代码（不要复制前面的部分）\n")

auth_code = input("请输入授权码: ").strip()

# 用授权码换取 token
flow.fetch_token(code=auth_code)

with open(TOKEN_FILE, 'wb') as f:
    pickle.dump(flow.credentials, f)

print(f"\n✅ 认证成功！")
print(f"权限范围: {flow.credentials.scopes}")
