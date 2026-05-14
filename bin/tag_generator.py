#!/usr/bin/env python3
import sqlite3
import threading
import re
import os
from PIL import Image

# 尝试导入 CLIP（可能失败）
try:
    from transformers import CLIPProcessor, CLIPModel

    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    print("⚠️ CLIP 不可用，将使用基于文件名的标签生成")

_model = None
_processor = None


def _load_model():
    global _model, _processor
    if CLIP_AVAILABLE and _model is None:
        print("🖼️ 加载 CLIP 模型...")
        _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _model.eval()


def get_image_tags_fallback(image_path):
    """回退方法：从文件名提取关键词作为标签"""
    name = os.path.basename(image_path)
    # 移除扩展名，分割常见分隔符
    words = re.split(r"[_.\- ]", os.path.splitext(name)[0])
    # 过滤短词，限制最多3个
    tags = [w for w in words if len(w) > 1][:3]
    if not tags:
        tags = ["图片"]
    return tags


def get_image_tags(image_path, candidates=None):
    if CLIP_AVAILABLE:
        if candidates is None:
            candidates = [
                "风景",
                "人物",
                "建筑",
                "科技",
                "美食",
                "动物",
                "夜景",
                "文化",
                "艺术",
                "自然",
            ]
        _load_model()
        if _model is not None:
            try:
                image = Image.open(image_path).convert("RGB")
                inputs = _processor(
                    text=candidates, images=image, return_tensors="pt", padding=True
                )
                outputs = _model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1).squeeze()
                top_idx = probs.argsort(descending=True)[:3]
                tags = [candidates[i] for i in top_idx if probs[i] > 0.1]
                if tags:
                    return tags
            except Exception as e:
                print(f"CLIP 识别失败: {e}")
    # 回退
    return get_image_tags_fallback(image_path)


def async_tag_file(file_path, file_id, tenant_id):
    tags = get_image_tags(file_path)
    if tags:
        db = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "UPDATE files SET auto_tags = ? WHERE id = ?", (",".join(tags), file_id)
        )
        conn.commit()
        conn.close()
        print(
            f"🏷️ 文件 {file_id} 标签: {tags} (来源: {'CLIP' if CLIP_AVAILABLE else '回退'})"
        )
