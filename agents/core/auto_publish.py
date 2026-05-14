from lib.unified_config import config
#!/usr/bin/env python3
"""自动发布到 YouTube - 调用 OpenClaw skill"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class YouTubeAutoPublisher:
    def __init__(self):
        self.skill_path = Path("/mnt/d/.openclaw/workspace/youtube_tasks/youtube-upload-skill")
        self.video_dir = Path("config.ROOT/web/videos")
        self.output_dir = Path("config.ROOT/output/youtube")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_latest_video(self):
        """获取最新视频"""
        videos = sorted(self.video_dir.glob("hk_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
        return videos[0] if videos else None
    
    def generate_metadata(self, video_path, topic):
        """生成 YouTube 元数据"""
        return {
            "title": f"香港身份新机遇｜{topic}全面解析（附申请攻略）",
            "description": f"🇭🇰 2026年{topic}迎来重大调整！本期视频全面解析最新政策变化。\n\n📌 本期重点：\n✅ 综合计分制最低分数：80分 → 75分\n✅ 新增人才清单：金融科技、人工智能、数据科学\n✅ 审批时间：6个月 → 3个月\n\n🔔 订阅频道，获取最新香港政策资讯！\n\n#香港优才计划 #香港身份 #香港移民",
            "tags": ["香港优才计划", "香港身份", "香港移民", "人才计划"],
            "privacyStatus": "unlisted",  # 先不公开，审核后改 public
            "categoryId": "27"  # 教育类
        }
    
    def publish(self, topic="香港优才计划"):
        """发布视频"""
        video = self.get_latest_video()
        if not video:
            print("❌ 没有找到视频")
            return False
        
        metadata = self.generate_metadata(video, topic)
        
        # 保存元数据供 skill 使用
        config_file = self.skill_path / "config" / "video_templates.json"
        with open(config_file, 'w') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 复制视频到 skill 目录
        import shutil
        target_video = self.skill_path / "scripts" / video.name
        shutil.copy(video, target_video)
        
        # 调用 OpenClaw skill 上传
        cmd = f"cd {self.skill_path}/scripts && node upload_video.js {target_video}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        print(f"✅ 发布结果: {result.stdout}")
        if result.stderr:
            print(f"⚠️ 错误: {result.stderr}")
        
        return result.returncode == 0

if __name__ == "__main__":
    publisher = YouTubeAutoPublisher()
    success = publisher.publish()
    print(f"发布{'成功' if success else '失败'}")
