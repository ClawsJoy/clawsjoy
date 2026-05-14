"""漫剧制作经验存入记忆"""
from lib.memory_simple import memory

def record_manju_success(script, scenes, character, video_path):
    memory.remember(
        f"漫剧成功|脚本:{script[:50]}|场景:{scenes}|角色:{character}|视频:{video_path}",
        category="manju_success"
    )

def get_best_practice():
    successes = memory.recall("漫剧成功", category="manju_success")
    if successes:
        return successes[-1]  # 最近一次成功经验
    return None

skill = Manju_experienceSkill()
