#!/usr/bin/env python3
"""话题角度管理器 - 避免重复"""

import json
from pathlib import Path
from datetime import datetime

ANGLES_FILE = Path("/mnt/d/clawsjoy/output/history/angles_used.json")

def load_used_angles():
    if ANGLES_FILE.exists():
        with open(ANGLES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_used_angle(angle, topic):
    used = load_used_angles()
    used.append({
        "angle": angle,
        "topic": topic,
        "date": datetime.now().isoformat()
    })
    # 只保留最近30条
    with open(ANGLES_FILE, 'w') as f:
        json.dump(used[-30:], f, ensure_ascii=False, indent=2)

def get_available_angles(topic):
    """获取未使用的角度"""
    used_angles = [a['angle'] for a in load_used_angles()]
    
    angles_pool = {
        "狮子山": [
            "创业精神：香港创业者如何以狮子山精神逆袭",
            "移民视角：新移民眼中的狮子山精神",
            "教育传承：狮子山精神如何教育下一代",
            "艺术表达：电影/音乐/文学中的狮子山精神",
            "时代变迁：狮子山精神在不同年代的演变",
            "国际视野：外国人如何看待香港狮子山精神",
            "日常生活：普通市民日常中的狮子山精神",
            "危机时刻：疫情期间狮子山精神的体现",
            "跨界融合：科技+人文+狮子山精神",
            "对比视角：狮子山精神vs其他城市精神"
        ],
        "default": [
            "政策解读", "申请攻略", "案例分析", "数据解读", "趋势预测"
        ]
    }
    
    pool = angles_pool.get(topic, angles_pool["default"])
    available = [a for a in pool if a not in used_angles]
    
    if not available:
        # 如果都用完了，重置并提示
        return pool[:3]
    return available
