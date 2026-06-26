#!/usr/bin/env python3
"""导出漫剧素材包 → Seedance/即梦 可用格式"""
import json, shutil
from pathlib import Path

PROJECT = "AI觉醒"
ASSETS = Path(f"data/assets/novels/{PROJECT}")
OUTPUT = Path(f"exports/seedance_{PROJECT}")

OUTPUT.mkdir(parents=True, exist_ok=True)

# 1. 剧本
script = OUTPUT / "剧本"
script.mkdir(exist_ok=True)
for f in (ASSETS / "storyboard").glob("*.mp4"):
    shutil.copy(f, script / f.name)

# 2. 角色参考图（取每角色道具版）
chars = OUTPUT / "角色"
chars.mkdir(exist_ok=True)
for role_dir in (ASSETS / "characters").iterdir():
    if role_dir.is_dir():
        role_name = role_dir.name
        images_dir = role_dir / "images"
        if images_dir.exists():
            for img in images_dir.glob("道具*"):
                dst = chars / f"{role_name}_道具.png"
                shutil.copy(img, dst)
                print(f"  角色: {role_name} → {dst.name}")
            for img in images_dir.glob("表情*"):
                dst = chars / f"{role_name}_{img.name}"
                shutil.copy(img, dst)

# 3. 场景图
scenes = OUTPUT / "场景"
scenes.mkdir(exist_ok=True)
for f in (ASSETS / "scenes").glob("场景*.png"):
    shutil.copy(f, scenes / f.name)
    print(f"  场景: {f.name}")

# 4. 分镜描述（文本）
with open(Path("memory/session_novel_ai_awakening_v2.json")) as f:
    session = json.load(f)
    
# 提取分镜内容
storyboard_text = ""
for item in session:
    if isinstance(item.get("assistant"), str) and "### 分镜" in item["assistant"]:
        storyboard_text = item["assistant"]
        break

(STORYBOARD := OUTPUT / "分镜剧本.txt").write_text(storyboard_text)

# 5. 导出清单
manifest = {
    "project": PROJECT,
    "chapters": 17,
    "characters": ["林浩", "艾丽卡", "无名"],
    "scenes": [str(p.name) for p in (ASSETS / "scenes").glob("*.png")],
    "export_time": __import__('datetime').datetime.now().isoformat()
}
(OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

import shutil
zip_path = OUTPUT.parent / f"{OUTPUT.name}.zip"
shutil.make_archive(str(OUTPUT), 'zip', str(OUTPUT))
print(f"\n✅ 导出完成 → {zip_path}")
