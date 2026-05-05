import re

with open("promo_api.py", "r") as f:
    content = f.read()

# 替换为 ffmpeg 直接生成
new_cmd = """
            # 使用 ffmpeg 直接生成视频
            video_path = f"/home/flybo/clawsjoy/web/videos/{city}_{int(__import__('time').time())}.mp4"
            cmd = f'ffmpeg -y -f lavfi -i color=c=blue:s=1920x1080:d=15 -vf "drawtext=text=\'{city}科技宣传片\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" -c:v libx264 {video_path}'
            os.system(cmd)
"""

# 简单替换
content = content.replace(
    "result = subprocess.run(cmd, capture_output=True)", "result = os.system(cmd)"
)

with open("promo_api.py", "w") as f:
    f.write(content)
print("✅ 已修改")
