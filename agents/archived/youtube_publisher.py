#!/usr/bin/env python3
"""YouTube 自动发布 Agent"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

class YouTubePublisher:
    def __init__(self):
        self.video_dir = Path("/mnt/d/clawsjoy/web/videos")
        self.output_dir = Path("/mnt/d/clawsjoy/output/youtube")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_latest_video(self):
        """获取最新生成的视频"""
        videos = sorted(self.video_dir.glob("hk_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
        return videos[0] if videos else None
    
    def generate_title(self, topic):
        """生成标题"""
        titles = [
            f"香港身份新机遇｜{topic}全面解析（附申请攻略）",
            f"{topic}｜2026最新政策解读｜分数降至75分",
            f"2026{topic}大变革！这些人直接加分｜香港身份攻略"
        ]
        return titles[0]
    
    def generate_description(self, topic, duration, key_points):
        """生成描述"""
        return f"""🇭🇰 2026年{topic}迎来重大调整！本期视频全面解析最新政策变化。

📌 本期重点：
{' '.join([f'✅ {p}' for p in key_points])}

🎯 谁适合申请？
• 本科及以上学历
• 2年以上工作经验
• 综合评分75分以上
• 想在港发展的专业人士

💡 申请攻略：
1️⃣ 自我评估分数
2️⃣ 准备学历、工作证明
3️⃣ 撰写来港计划书
4️⃣ 在线提交申请

🔔 订阅频道，获取最新香港政策资讯！

#香港优才计划 #香港身份 #香港移民 #香港人才计划

📩 评论留言你的分数，帮你评估成功率！
"""
    
    def generate_tags(self, topic):
        """生成标签"""
        base_tags = ["香港优才计划", "香港身份", "香港移民", "香港人才计划", "香港签证"]
        return base_tags
    
    def generate_thumbnail_text(self, topic):
        """生成缩略图文字"""
        return f"香港身份新机遇 | {topic[:10]} | 附攻略"
    
    def save_metadata(self, video_path, topic, duration, key_points):
        """保存元数据供手动上传"""
        metadata = {
            "video": str(video_path),
            "title": self.generate_title(topic),
            "description": self.generate_description(topic, duration, key_points),
            "tags": self.generate_tags(topic),
            "thumbnail_text": self.generate_thumbnail_text(topic),
            "generated_at": datetime.now().isoformat()
        }
        
        output_file = self.output_dir / f"metadata_{video_path.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return output_file
    
    def prepare_for_publish(self, topic="香港优才计划", key_points=None):
        """准备发布（生成所有元数据）"""
        if key_points is None:
            key_points = [
                "综合计分制最低分数：80分 → 75分",
                "新增人才清单：金融科技、人工智能、数据科学",
                "审批时间：6个月 → 3个月",
                "2025年获批数据：3421人获批，成功率38%"
            ]
        
        video = self.get_latest_video()
        if not video:
            print("❌ 没有找到视频")
            return None
        
        # 获取视频时长
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video)],
            capture_output=True, text=True
        )
        duration = float(result.stdout.strip()) if result.stdout else 0
        
        # 保存元数据
        metadata_file = self.save_metadata(video, topic, duration, key_points)
        
        print(f"✅ 已准备发布: {video.name}")
        print(f"   时长: {duration:.0f} 秒")
        print(f"   元数据: {metadata_file}")
        print(f"   标题: {self.generate_title(topic)}")
        
        return metadata_file

if __name__ == "__main__":
    publisher = YouTubePublisher()
    publisher.prepare_for_publish()
