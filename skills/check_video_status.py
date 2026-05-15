import pickle
from googleapiclient.discovery import build
from lib.memory_simple import memory
from skills.satisfaction import skill as satisfaction

class CheckVideoStatusSkill:
    name = "check_video_status"
    description = "检查已上传视频的状态，自动回写满意度"

    def execute(self, params):
        with open('data/youtube_token.pickle', 'rb') as f:
            creds = pickle.load(f)
        youtube = build('youtube', 'v3', credentials=creds)

        # 从记忆获取所有上传过的视频
        history = memory.recall("video_uploaded", category="video_history")
        
        results = []
        for record in history:
            # 提取 video_id
            if "video_id:" not in record:
                continue
            video_id = record.split("video_id:")[1].split("|")[0].strip()
            
            try:
                resp = youtube.videos().list(part='status,snippet', id=video_id).execute()
                if not resp['items']:
                    score = 1
                    reason = "视频已被删除"
                else:
                    privacy = resp['items'][0]['status']['privacyStatus']
                    if privacy == 'public':
                        score = 5
                        reason = "视频已公开"
                    elif privacy == 'unlisted':
                        score = 3
                        reason = "视频为不公开"
                    else:
                        score = 0
                        reason = f"状态: {privacy}"
                
                # 回写满意度
                satisfaction.execute({
                    'goal': f"video:{video_id}",
                    'score': score,
                    'comment': reason
                })
                results.append({"video_id": video_id, "score": score, "reason": reason})
            except Exception as e:
                results.append({"video_id": video_id, "error": str(e)})
        
        return {"checked": len(results), "results": results}

skill = CheckVideoStatusSkill()
