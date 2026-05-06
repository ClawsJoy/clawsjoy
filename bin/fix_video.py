import re

with open('promo_api.py', 'r') as f:
    content = f.read()

# 找到视频合成部分并替换
old_block = r"concat_file = f\"/tmp/concat_.*?subprocess\.run\(cmd, shell=True\).*?os\.remove\(concat_file\)"
new_block = '''# 多图轮播（filter方式）
            filter_cmd = ""
            for i, img in enumerate(images[:6]):
                filter_cmd += f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}];"
            filter_cmd += "".join([f"[v{i}]" for i in range(len(images[:6]))]) + f"concat=n={len(images[:6])}:v=1:a=0,format=yuv420p[v]"
            cmd = f"ffmpeg " + " ".join([f"-loop 1 -t 2.5 -i {img}" for img in images[:6]]) + f" -filter_complex \"{filter_cmd}\" -map \"[v]\" -c:v libx264 -pix_fmt yuv420p -y {video_path}\""""

content = re.sub(old_block, new_block, content, flags=re.DOTALL)

with open('promo_api.py', 'w') as f:
    f.write(content)
print("✅ 视频合成已修复")
