from lib.smart_config import smart_config
"""批量迁移技能 - 从旧格式到新架构"""
import json
from pathlib import Path

# 定义要迁移的技能
skills_to_migrate = [
    # 数学技能
    {"name": "add", "category": "math", "description": "两数相加", "input": {"a": "number", "b": "number"}},
    {"name": "multiply", "category": "math", "description": "两数相乘", "input": {"a": "number", "b": "number"}},
    {"name": "divide", "category": "math", "description": "两数相除", "input": {"a": "number", "b": "number"}},
    
    # 文本技能
    {"name": "text_processor", "category": "text", "description": "文本处理", "input": {"text": "string"}},
    {"name": "json_parser", "category": "data", "description": "JSON解析", "input": {"data": "string"}},
    
    # 图像技能
    {"name": "remove_bg", "category": "image", "description": "移除背景", "input": {"image_path": "string"}},
    {"name": "spider", "category": "image", "description": "图片采集", "input": {"keyword": "string"}},
    
    # 视频技能
    {"name": "add_subtitles", "category": "video", "description": "添加字幕", "input": {"video_path": "string"}},
    {"name": "video_uploader", "category": "video", "description": "上传视频", "input": {"video_path": "string"}},
    
    # 网络技能
    {"name": "youtube_uploader", "category": "network", "description": "YouTube上传", "input": {"video_path": "string"}},
]

manifest_dir = Path("src/skills/manifests/atomic")
manifest_dir.mkdir(parents=True, exist_ok=True)

for skill in skills_to_migrate:
    manifest = {
        "name": skill["name"],
        "type": "atomic",
        "version": "1.0.0",
        "description": skill["description"],
        "category": skill["category"],
        "author": "ClawsJoy",
        "compatible_with": ["openclaw", "clawsjoy"],
        "input_schema": {k: {"type": v, "required": True} for k, v in skill["input"].items()},
        "output_schema": {"success": {"type": "boolean"}}
    }
    
    manifest_file = manifest_dir / f"{skill['name']}.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ 生成清单: {skill['name']}.json")

print(f"\n共生成 {len(skills_to_migrate)} 个技能清单")
