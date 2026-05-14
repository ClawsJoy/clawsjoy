#!/usr/bin/env python3
"""技能统计"""
import os
from pathlib import Path

skills_dir = Path("skills")
if not skills_dir.exists():
    print("技能目录不存在")
    exit(1)

skills = [f for f in skills_dir.glob("*.py") if f.stem != "__init__"]
categories = {
    "core": ["do_anything", "calibrated_executor", "quality_gate", "closed_loop_executor", "design_executor", "improve_executor", "user_task_executor"],
    "math": ["add", "multiply", "divide", "calculator"],
    "image": ["remove_bg", "spider", "image_slideshow", "character_designer", "ai_image", "ai_image_gen"],
    "video": ["manju_maker", "video_uploader", "add_subtitles", "ffmpeg_video", "check_video_status", "video_description", "video_public"],
    "text": ["text_processor", "json_parser", "hot_dual_script", "hot_script", "hot_short_script", "script_writer", "prompt_optimizer"],
    "hot": ["hot_analyzer", "hot_collector"],
    "self_heal": ["self_heal", "self_healer", "self_debug", "self_calibrator", "self_evaluator", "self_reviewer", "self_designer_v4", "error_analyzer", "error_knowledge_base", "fix_validator"],
    "memory": ["memory", "knowledge_ingest"],
    "network": ["tts", "youtube_uploader", "youtube_publisher", "whisper_transcribe"],
    "data": ["file_processor", "file_service_skill", "queue", "router", "search", "url_discovery"],
    "quality": ["quality_executor", "quality_gate", "satisfaction", "release_decision"],
    "code_gen": ["code_agent_v7", "skill_generator", "skill_generator_v2"],
    "other": ["requirement_analyzer", "intent_parser", "state_manager", "task_optimizer", "assemble_from_library", "auto_operator"]
}

print("=" * 50)
print("ClawsJoy 原子技能统计")
print("=" * 50)

total = 0
for cat, names in categories.items():
    count = len([s for s in skills if s.stem in names])
    total += count
    print(f"{cat:12} : {count:2} 个技能")

print("-" * 50)
print(f"{'总计':12} : {total:2} 个技能")
print("=" * 50)

# 显示未分类的技能
classified = set()
for names in categories.values():
    classified.update(names)
unclassified = [s.stem for s in skills if s.stem not in classified]
if unclassified:
    print(f"\n未分类技能: {unclassified}")
