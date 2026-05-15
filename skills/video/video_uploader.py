import os
import pickle
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploaderSkill:
    name = "video_uploader"
    description = "上传视频到 YouTube"

    def _get_credentials(self):
        token_file = "data/youtube_token.pickle"
        creds = None
        if os.path.exists(token_file):
            with open(token_file, "rb") as f:
                creds = pickle.load(f)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
                            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    },
                    ["https://www.googleapis.com/auth/youtube.upload"]
                )
                creds = flow.run_local_server(port=0)
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
        return creds

    def _is_duplicate(self, title):
        """检查是否重复上传"""
        from lib.memory_simple import memory
        history = memory.recall("uploaded", category="video_uploads")
        for record in history:
            if f"|{title}|" in record:
                return True
        return False

    def execute(self, params):
        video_file = params.get("video_file", "")
        title = params.get("title", "AI Generated Video")
        description = params.get("description", "")
        privacy = params.get("privacy", "unlisted")  # 默认不公开

        # 检查重复
        if self._is_duplicate(title):
            return {"error": f"重复上传: {title} 已存在", "duplicate": True}

        if not video_file or not os.path.exists(video_file):
            return {"error": f"Video file not found: {video_file}"}

        try:
            creds = self._get_credentials()
            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": privacy}
            }

            media = MediaFileUpload(video_file, chunksize=1024*1024, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            response = None
            retry = 0
            while response is None and retry < 3:
                try:
                    status, response = request.next_chunk()
                    if status:
                        print(f"上传进度: {int(status.progress() * 100)}%")
                except Exception as e:
                    retry += 1
                    print(f"重试 {retry}/3: {e}")
                    time.sleep(5)

            if response:
                from lib.memory_simple import memory
                memory.remember(
                    f"uploaded:{response['id']}|{title}|{privacy}",
                    category="video_uploads"
                )
                return {
                    "success": True,
                    "video_id": response["id"],
                    "video_url": f"https://youtu.be/{response['id']}"
                }
            else:
                return {"error": "上传失败，超过重试次数"}

        except Exception as e:
            return {"error": str(e)}

skill = YouTubeUploaderSkill()
