import requests
from bs4 import BeautifulSoup
from lib.proxy_helper import get_session, is_local_url

class SpiderSkill:
    name = "spider"
    description = "网页采集（智能代理）"
    version = "1.0.0"
    category = "crawler"

    def execute(self, params):
        mode = params.get("mode", "webpage")
        
        if mode == "webpage":
            url = params.get("url", "")
            if not url:
                return {"error": "url required"}
            return self._fetch_webpage(url)
        
        elif mode == "images":
            keyword = params.get("keyword", "")
            count = params.get("count", 5)
            if not keyword:
                return {"error": "keyword required"}
            return self._fetch_images(keyword, count)
        
        return {"error": f"Unknown mode: {mode}"}
    
    def _fetch_webpage(self, url):
        try:
            # 本地地址用直连，国外用代理
            use_proxy = not is_local_url(url)
            session = get_session(use_proxy)
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            for s in soup(["script", "style"]):
                s.decompose()
            text = soup.get_text()
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            return {
                "success": True,
                "title": soup.title.string if soup.title else "",
                "content": "\n".join(lines[:300])
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_images(self, keyword, count):
        images = []
        import os
        os.makedirs('output/images', exist_ok=True)
        
        for i in range(count):
            url = f"https://source.unsplash.com/featured/?{keyword}&w=1280&h=720&sig={i}"
            try:
                # Unsplash 是国外网站，走代理
                session = get_session(use_proxy=True)
                resp = session.get(url, timeout=30)
                if resp.status_code == 200:
                    img_path = f"output/images/{keyword}_{i}.jpg"
                    with open(img_path, 'wb') as f:
                        f.write(resp.content)
                    images.append(img_path)
            except Exception as e:
                print(f"图片下载失败: {e}")
        return {"success": True, "images": images, "count": len(images)}

skill = SpiderSkill()
