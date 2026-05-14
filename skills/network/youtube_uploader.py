import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploaderSkill:
    name = "youtube_uploader"
    description = "上传视频到 YouTube 并记录到系统"

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
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
        return creds

    def execute(self, params):
        video_file = params.get("video_file", "")
        title = params.get("title", "AI Generated Video")
        description = params.get("description", "")
        privacy = params.get("privacy", "unlisted")
        tags = params.get("tags", [])
        category_id = params.get("category_id", "22")  # 22 = People & Blogs

        if not video_file or not os.path.exists(video_file):
            return {"error": f"Video file not found: {video_file}"}

        try:
            creds = self._get_credentials()
            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            response = request.execute()

            video_id = response["id"]
            video_url = f"https://youtu.be/{video_id}"

            # ✅ 记录上传历史到记忆
            from lib.memory_simple import memory
            memory.remember(
                f"video_uploaded: {video_id} | title: {title} | privacy: {privacy} | file: {video_file}",
                category="video_history"
            )

            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url,
                "title": title,
                "privacy": privacy
            }
        except Exception as e:
            return {"error": str(e)}

skill = YouTubeUploaderSkill()
