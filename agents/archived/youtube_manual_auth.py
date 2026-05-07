#!/usr/bin/env python3
"""手动授权码模式 - 不需要本地服务器"""

import pickle
import webbrowser
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

CRED_DIR = Path("/mnt/d/clawsjoy/config/youtube")
TOKEN_FILE = CRED_DIR / "token.pickle"
SECRET_FILE = CRED_DIR / "client_secrets.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

print("🔐 YouTube OAuth 认证")
print("=" * 50)

# 读取配置
with open(SECRET_FILE, 'r') as f:
    import json
    config = json.load(f)
    client_id = config['installed']['client_id']
    client_secret = config['installed']['client_secret']

# 手动构建授权 URL
auth_url = (
    f"https://accounts.google.com/o/oauth2/auth?"
    f"client_id={client_id}&"
    f"redirect_uri=http://localhost&"
    f"response_type=code&"
    f"scope={' '.join(SCOPES)}&"
    f"access_type=offline&"
    f"prompt=consent"
)

print("\n📋 请复制以下链接到浏览器打开：")
print("=" * 50)
print(auth_url)
print("=" * 50)
print("\n👉 在浏览器中登录并授权后，地址栏会显示：")
print("   http://localhost/?code=4/xxxxxxxxxxx")
print("\n👉 复制 code= 后面的那一串代码（不要复制前面的部分）")
print("   code= 后面的就是授权码\n")

auth_code = input("请输入授权码: ").strip()

# 用授权码换取 token
from google.oauth2.credentials import Credentials
import requests

token_url = "https://oauth2.googleapis.com/token"
data = {
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': 'http://localhost',
    'grant_type': 'authorization_code'
}

resp = requests.post(token_url, data=data)
if resp.status_code == 200:
    token_data = resp.json()
    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        client_id=client_id,
        client_secret=client_secret,
        token_uri=token_url,
        scopes=SCOPES
    )
    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)
    print(f"\n✅ 认证成功！令牌已保存到 {TOKEN_FILE}")
else:
    print(f"\n❌ 认证失败: {resp.text}")
