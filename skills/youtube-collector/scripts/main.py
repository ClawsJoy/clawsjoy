"""YouTube  - """

import json
from datetime import datetime
from typing import Dict, List, Optional

import requests


class YouTubeCollectorSkill:

    def _search_tech_trends(self, params: Dict) -> Dict:
        """搜索科技类热门视频（使用关键词）"""
        limit = params.get("limit", 10)
        query = params.get("query", "AI technology innovation future")

        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": limit,
                "order": "viewCount",
                "key": self.YOUTUBE_API_KEY,
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.status_code}"}

            data = response.json()
            items = data.get("items", [])

            results = []
            for item in items:
                results.append(
                    {
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    }
                )

            return {
                "success": True,
                "query": query,
                "count": len(results),
                "trending": results,
                "collected_at": __import__("datetime").datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    name = "youtube_collector"
    description = "采集 YouTube 频道数据、热门话题、视频信息"
    version = "2.0.0"
    category = "youtube"

    # YouTube API 配置（使用公开 API，不需要认证）
    YOUTUBE_API_KEY = "AIzaSyAxAw6dkgFIGgC8G_A2agjwAzpmUuxpZcU"

    # 热门话题地区
    REGIONS = {
        "US": "美国",
        "GB": "英国",
        "JP": "日本",
        "KR": "韩国",
        "IN": "印度",
        "BR": "巴西",
    }

    def execute(self, params: Dict) -> Dict:
        action = params.get("action", "channel_data")

        if action == "channel_data":
            return self._collect_channel_data(params)
        elif action == "trending":
            return self._search_tech_trends(params)
            return self._collect_trending(params)
        elif action == "search":
            return self._search_videos(params)
        elif action == "video_details":
            return self._get_video_details(params)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _collect_channel_data(self, params: Dict) -> Dict:
        """采集频道数据（需要用户认证）"""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        from core.lib.user_crypto import UserCrypto

        user_id = params.get("user_id", "")
        password = params.get("password", "")

        if not user_id or not password:
            return {"success": False, "error": "user_id and password required"}

        try:
            crypto = UserCrypto(user_id, password)
            creds_data = crypto.decrypt("youtube_credentials")

            if not creds_data:
                return {"success": False, "error": "YouTube credentials not found"}

            creds = Credentials(
                token=None,
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret"),
            )

            youtube = build("youtube", "v3", credentials=creds)

            # 获取频道信息
            channel_response = (
                youtube.channels().list(part="snippet,statistics", mine=True).execute()
            )

            if not channel_response.get("items"):
                return {"success": False, "error": "No channel found"}

            channel = channel_response["items"][0]

            # 获取最近视频
            videos_response = (
                youtube.search()
                .list(
                    part="snippet",
                    channelId=channel["id"],
                    order="date",
                    type="video",
                    maxResults=10,
                )
                .execute()
            )

            result = {
                "success": True,
                "channel": {
                    "id": channel["id"],
                    "title": channel["snippet"]["title"],
                    "description": channel["snippet"]["description"][:200],
                    "subscriber_count": int(
                        channel["statistics"].get("subscriberCount", 0)
                    ),
                    "video_count": int(channel["statistics"].get("videoCount", 0)),
                    "view_count": int(channel["statistics"].get("viewCount", 0)),
                    "collected_at": datetime.now().isoformat(),
                },
                "recent_videos": [],
            }

            for item in videos_response.get("items", []):
                result["recent_videos"].append(
                    {
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                    }
                )

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _collect_trending(self, params: Dict) -> Dict:
        """采集 YouTube 热门话题（支持类别筛选）"""
        region = params.get("region", "US")
        limit = params.get("limit", 20)
        category = params.get("category", "20")  # 20 = 科技

        # 科技类别ID映射
        category_map = {
            "tech": "20",  # 科技
            "gaming": "20",  # 游戏（也属科技）
            "science": "20",  # 科学
            "all": "0",
        }

        cat_id = category_map.get(category, category)

        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": region,
                "maxResults": limit,
                "videoCategoryId": cat_id,
                "key": self.YOUTUBE_API_KEY,
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.status_code}"}

            data = response.json()
            items = data.get("items", [])

            trending = []
            for item in items:
                trending.append(
                    {
                        "id": item["id"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "views": int(item["statistics"].get("viewCount", 0)),
                        "likes": int(item["statistics"].get("likeCount", 0)),
                        "comments": int(item["statistics"].get("commentCount", 0)),
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    }
                )

            return {
                "success": True,
                "region": region,
                "category": cat_id,
                "count": len(trending),
                "trending": trending,
                "collected_at": __import__("datetime").datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_videos(self, params: Dict) -> Dict:
        """搜索视频"""
        query = params.get("query", "")
        limit = params.get("limit", 10)

        if not query:
            return {"success": False, "error": "query required"}

        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": limit,
                "key": self.YOUTUBE_API_KEY,
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.status_code}"}

            data = response.json()
            items = data.get("items", [])

            results = []
            for item in items:
                results.append(
                    {
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    }
                )

            return {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_video_details(self, params: Dict) -> Dict:
        """获取视频详情"""
        video_ids = params.get("video_ids", [])

        if not video_ids:
            return {"success": False, "error": "video_ids required"}

        video_ids_str = ",".join(video_ids)

        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,statistics",
                "id": video_ids_str,
                "key": self.YOUTUBE_API_KEY,
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.status_code}"}

            data = response.json()

            return {"success": True, "videos": data.get("items", [])}

        except Exception as e:
            return {"success": False, "error": str(e)}


# 技能实例
skill = YouTubeCollectorSkill()
