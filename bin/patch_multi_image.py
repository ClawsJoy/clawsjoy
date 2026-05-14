# 替换视频合成部分
import re

with open('promo_api.py', 'r') as f:
    content = f.read()

# 找到视频合成命令，替换为多图轮播
old_cmd = r'cmd = f\'ffmpeg -loop 1 -i "{images\[0\]}" -c:v libx264 -t 5 -pix_fmt yuv420p -y "{video_path}"\''

new_cmd = '''# 多图轮播
            concat_file = f"/tmp/concat_{int(time.time())}.txt"
            with open(concat_file, 'w') as cf:
                for img in images[:6]:
                    cf.write(f"file '{img}\\n")\\n
                    cf.write(f"duration 2.5\\n")
            cmd = f"ffmpeg -f concat -safe 0 -i {concat_file} -c:v libx264 -pix_fmt yuv420p -y {video_path}"
            subprocess.run(cmd, shell=True)
            os.remove(concat_file)'''

content = re.sub(old_cmd, new_cmd, content)

with open('promo_api.py', 'w') as f:
    f.write(content)
print("✅ 已升级为多图轮播")
