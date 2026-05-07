#!/usr/bin/env python3
"""YouTube 完整权限认证"""

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

print("🔐 开始 YouTube 完整权限认证")
print("请求的权限:")
for scope in SCOPES:
    print(f"  - {scope}")

# 删除旧令牌
if TOKEN_FILE.exists():
    TOKEN_FILE.unlink()
    print("✅ 已删除旧令牌")

flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
creds = flow.run_local_server(port=8088, open_browser=True)

with open(TOKEN_FILE, 'wb') as f:
    pickle.dump(creds, f)

print(f"\n✅ 认证成功！")
print(f"权限范围: {creds.scopes}")
