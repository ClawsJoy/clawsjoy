"""视觉日志 - 每张图自动描述并存档"""
import base64, requests, json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("data/assets/novels/AI觉醒/vision_log.jsonl")

def describe_and_log(image_path, prompt_used="", tags=""):
    """用 llava 描述图片并记录日志"""
    with open(image_path, 'rb') as f:
        img = base64.b64encode(f.read()).decode()
    
    r = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llava:latest',
        'prompt': '详细描述：构图、主体、光线、色调、风格、画质。一句话总结。',
        'images': [img], 'stream': False
    }, timeout=120)
    
    desc = r.json().get('response', '描述失败')
    
    log = {
        "time": datetime.now().isoformat(),
        "file": str(image_path),
        "prompt": prompt_used,
        "llava_description": desc,
        "tags": tags
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log, ensure_ascii=False) + '\n')
    
    return desc

def query_log(keyword="", limit=5):
    """查询日志"""
    if not LOG_FILE.exists():
        return []
    results = []
    with open(LOG_FILE) as f:
        for line in f:
            if keyword in line:
                results.append(json.loads(line))
    return results[-limit:]

def compare_two(path1, path2):
    """对比两张图的差异"""
    desc1 = describe_and_log(path1)
    desc2 = describe_and_log(path2)
    return f"图1: {desc1[:200]}\n\n图2: {desc2[:200]}"
