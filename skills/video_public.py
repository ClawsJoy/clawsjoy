import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.smart_config import smart_config
"""将视频转为公开"""
import pickle
from googleapiclient.discovery import build

class VideoPublicSkill:
    name = "video_public"
    description = "将不公开视频转为公开"

    def execute(self, params):
        video_id = params.get("video_id", "")

        with open('data/youtube_token.pickle', 'rb') as f:
            creds = pickle.load(f)

        youtube = build('youtube', 'v3', credentials=creds)

        youtube.videos().update(
            part='status',
            body={'id': video_id, 'status': {'privacyStatus': 'public'}}
        ).execute()

        return {"success": True, "video_id": video_id, "status": "public"}

skill = VideoPublicSkill()
