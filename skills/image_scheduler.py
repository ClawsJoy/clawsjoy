#!/usr/bin/env python3
"""图片调度器 - 优先级调度"""

import json
from pathlib import Path
import random

class ImageScheduler:
    def __init__(self, tenant_id="1"):
        self.tenant_id = tenant_id
        self.user_image_dir = Path(f"/mnt/d/clawsjoy/tenants/tenant_{tenant_id}/library/images")
        self.unsplash_dir = Path("/mnt/d/clawsjoy/web/images/unsplash")
        self.ai_generated_dir = Path("/mnt/d/clawsjoy/web/images/ai_generated")
    
    def get_user_images(self, keyword=None):
        """获取用户自己的照片（优先级1）"""
        if not self.user_image_dir.exists():
            return []
        
        images = list(self.user_image_dir.glob("*.jpg")) + list(self.user_image_dir.glob("*.png"))
        
        # 根据关键词筛选
        if keyword and keyword != "all":
            filtered = []
            for img in images:
                if keyword in img.stem.lower():
                    filtered.append(str(img))
            return filtered if filtered else [str(img) for img in images[:6]]
        
        return [str(img) for img in images[:6]]
    
    def get_unsplash_images(self, keyword, count=6):
        """Unsplash 实景图（优先级2）"""
        # 这里调用已有的 Unsplash 采集
        from unsplash_fetcher import fetch_images
        return fetch_images(keyword, count)
    
    def get_ai_images(self, script, count=4):
        """AI 生成图文（优先级3）"""
        # 这里调用文案生图
        from text_to_image import generate_matched_images
        return generate_matched_images(script)[:count]
    
    def schedule(self, request):
        """调度主入口"""
        topic = request.get("topic", "")
        script = request.get("script", "")
        user_feedback = request.get("user_feedback", "")
        
        # 关键词检测
        keywords = ["照片", "我的图", "本地", "草稿", "上传", "拍照"]
        need_user_images = any(kw in topic for kw in keywords)
        
        # 图文类检测
        graphic_keywords = ["图文", "海报", "插画", "设计图", "AI图"]
        need_ai_images = any(kw in topic for kw in graphic_keywords)
        
        result = []
        
        # 优先级1：用户自己的照片
        if need_user_images or user_feedback == "wrong":
            result = self.get_user_images()
            if result:
                return {"source": "user", "images": result, "message": "已使用您的本地照片"}
        
        # 优先级2：Unsplash 实景图
        if not result:
            result = self.get_unsplash_images(topic, 6)
            if result:
                return {"source": "unsplash", "images": result, "message": "已使用实景图库"}
        
        # 优先级3：AI 图文生成
        if need_ai_images or (not result and script):
            result = self.get_ai_images(script, 4)
            if result:
                return {"source": "ai", "images": result, "message": "已生成匹配图文"}
        
        return {"source": "none", "images": [], "message": "暂无可用图片"}
    
    def record_feedback(self, topic, approved, source):
        """记录用户反馈，用于优化调度"""
        feedback_file = Path("/mnt/d/clawsjoy/data/image_feedback.json")
        data = []
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                data = json.load(f)
        
        data.append({"topic": topic, "approved": approved, "source": source})
        with open(feedback_file, 'w') as f:
            json.dump(data[-100:], f, ensure_ascii=False, indent=2)  # 只保留最近100条

if __name__ == "__main__":
    scheduler = ImageScheduler()
    
    # 测试
    test_cases = [
        {"topic": "香港优才计划政策"},
        {"topic": "用我的照片做香港视频"},
        {"topic": "做一张香港图文海报"}
    ]
    
    for req in test_cases:
        result = scheduler.schedule(req)
        print(f"{req['topic']} → {result['source']}: {result['message']}")
