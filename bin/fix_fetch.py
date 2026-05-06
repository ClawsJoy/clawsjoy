import re

with open('promo_api.py', 'r') as f:
    content = f.read()

# 替换 fetch_images 函数
old_func = r'def fetch_images\(keyword, count=8\):.*?(?=\n\S|$)'
new_func = '''def fetch_images(keyword, count=8):
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": keyword, "per_page": count, "orientation": "landscape"}
    images = []
    try:
        resp = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            for photo in resp.json().get('results', []):
                img_url = photo['urls']['regular']
                img_data = requests.get(img_url).content
                img_name = f"{uuid.uuid4().hex}.jpg"
                img_path = IMAGE_DIR / img_name
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                images.append(str(img_path))
                print(f"✅ 采集图片: {img_name}")
            return images
    except Exception as e:
        print(f"采集错误: {e}")
    return images'''

content = re.sub(old_func, new_func, content, flags=re.DOTALL)

with open('promo_api.py', 'w') as f:
    f.write(content)
print("✅ fetch_images 已修复")
