from lib.smart_config import smart_config
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploaderSkill:
    name = "youtube_uploader"
    description = "上传视频到 YouTube"
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
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
                flow = InstalledAppFlow.from_client_secrets_file(
                    "config/youtube/client_secrets.json", self.SCOPES)
                # 使用本地服务器接收回调
                creds = flow.run_local_server(port=8080)
            
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
        
        return creds
    
    def execute(self, params):
        video_file = params.get("video_file", "")
        title = params.get("title", "ClawsJoy Video")
        description = params.get("description", "")
        privacy = params.get("privacy", "private")
        tags = params.get("tags", [])
        
        if not video_file or not os.path.exists(video_file):
            return {"success": False, "error": f"Video file not found: {video_file}"}
        
        try:
            creds = self._get_credentials()
            youtube = build("youtube", "v3", credentials=creds)
            
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "22"
                },
                "status": {
                    "privacyStatus": privacy
                }
            }
            
            media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            return {
                "success": True,
                "video_id": response["id"],
                "message": f"Video uploaded: https://youtu.be/{response['id']}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = YouTubeUploaderSkill()
