#!/usr/bin/env python3
"""YouTube 上传器 - 租户隔离版"""

import pickle
import sys
import json
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_tenant_config(tenant_id):
    """获取租户配置目录"""
    tenant_dir = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}")
    config_dir = tenant_dir / "config" / "youtube"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_credentials(tenant_id):
    """获取租户凭证（自动读取或触发授权）"""
    config_dir = get_tenant_config(tenant_id)
    token_file = config_dir / "token.pickle"
    
    if token_file.exists():
        with open(token_file, 'rb') as f:
            return pickle.load(f)
    
    # 自动触发首次授权
    return auth_tenant(tenant_id)

def auth_tenant(tenant_id):
    """自动授权租户（首次运行时）"""
    config_dir = get_tenant_config(tenant_id)
    client_secret = config_dir / "client_secrets.json"
    
    if not client_secret.exists():
        return {"success": False, "error": f"请将 client_secrets.json 放到 {config_dir}"}
    
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
    creds = flow.run_local_server(port=0)
    
    token_file = config_dir / "token.pickle"
    with open(token_file, 'wb') as f:
        pickle.dump(creds, f)
    
    return creds

def upload_video(tenant_id, title=None, privacy="public"):
    """租户上传视频"""
    config_dir = get_tenant_config(tenant_id)
    token_file = config_dir / "token.pickle"
    
    if not token_file.exists():
        return {"success": False, "error": f"租户 {tenant_id} 未授权，请先完成 OAuth"}
    
    with open(token_file, 'rb') as f:
        creds = pickle.load(f)
    
    # 获取租户最新的视频
    video_dir = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/videos")
    video_dir.mkdir(parents=True, exist_ok=True)
    videos = sorted(video_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not videos:
        # 尝试全局视频目录
        global_video_dir = Path("/mnt/d/clawsjoy/web/videos")
        videos = sorted(global_video_dir.glob("promo_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not videos:
        return {"success": False, "error": "没有找到视频"}
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title or f'ClawsJoy 视频 - 租户 {tenant_id}',
            'description': f'由 ClawsJoy 自动生成\n租户ID: {tenant_id}',
            'categoryId': '27'
        },
        'status': {'privacyStatus': privacy}
    }
    
    media = MediaFileUpload(str(videos[0]), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = request.execute()
    
    return {"success": True, "url": f"https://youtu.be/{response['id']}", "video_id": response['id']}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", default="tenant_1")
    parser.add_argument("--auth", action="store_true")
    parser.add_argument("--title", default=None)
    args = parser.parse_args()
    
    if args.auth:
        result = auth_tenant(args.tenant)
        print(json.dumps({"success": True, "message": f"租户 {args.tenant} 授权完成"}))
    else:
        result = upload_video(args.tenant, args.title)
        print(json.dumps(result, ensure_ascii=False))
