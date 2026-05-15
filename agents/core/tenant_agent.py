from lib.unified_config import config
#!/usr/bin/env python3
"""TenantAgent - 完整版"""

import json
import re
import requests
import subprocess
from pathlib import Path
from keyword_learner import KeywordLearner
from keyword_index import KeywordIndex
from memory_manager import MemoryManager

class TenantAgent:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.keyword_learner = KeywordLearner()
        self.keyword_index = KeywordIndex(tenant_id)
        self.memory = MemoryManager(tenant_id)
        self.config_file = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/agent_config.json")
        self._load_config()
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {"tenant_id": self.tenant_id, "alert_webhooks": {}}
    
    def process(self, user_input):
        print(f"📥 处理: {user_input[:50]}...")
        
        # 1. 学习关键词
        self.keyword_learner.extract_candidates(user_input)
        learned = self.keyword_learner.auto_learn()
        if learned:
            print(f"📚 新学习: {learned}")
        
        # 2. 记录记忆
        self.memory.add(user_input, "conversation")
        
        # 3. 分发
        lower = user_input.lower()
        if "统计" in lower or "关键词" in lower:
            return self._stats()
        if any(k in lower for k in ["制作", "生成", "宣传片"]):
            return self._video(user_input)
        if "上传" in lower and "youtube" in lower:
            return self._upload()
        if "告警" in lower or "钉钉" in lower:
            return self._alert(user_input)
        return self._chat(user_input)
    
    def _stats(self):
        stats = self.keyword_learner.get_stats()
        return {"type": "result", "message": f"📊 关键词库: {stats['total_keywords']} 个, 待学习: {stats['pending_count']} 个", "data": stats}
    
    def _video(self, user_input):
        topic = next((c for c in ["香港", "上海", "深圳", "北京"] if c in user_input), "香港")
        try:
            resp = requests.post("http://localhost:8108/api/promo/make", json={"topic": topic, "duration": 30}, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return {"type": "result", "message": "✅ 视频已生成", "data": {"video_url": data.get("video_url")}}
        except Exception as e:
            return {"type": "result", "message": f"生成失败: {str(e)}"}
        return {"type": "result", "message": "生成失败"}
    
    def _upload(self):
        try:
            result = subprocess.run(["python3", "/mnt/d/clawsjoy/agents/youtube_uploader.py", "--tenant", self.tenant_id], capture_output=True, text=True, timeout=300)
            return {"type": "result", "message": "✅ 已上传" if result.returncode == 0 else "上传失败"}
        except:
            return {"type": "result", "message": "上传异常"}
    
    def _alert(self, user_input):
        url_match = re.search(r'https?://[^\s]+', user_input)
        if not url_match:
            return {"type": "text", "message": "请提供 Webhook URL"}
        platform = "dingtalk" if "钉钉" in user_input else "feishu" if "飞书" in user_input else "dingtalk"
        self.config.setdefault("alert_webhooks", {})[platform] = url_match.group()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        return {"type": "result", "message": f"✅ 已配置 {platform} 告警"}
    
    def _chat(self, user_input):
        try:
            resp = requests.post("http://localhost:11434/api/generate", json={"model": config.LLM["fast_model"], "prompt": user_input, "stream": False, "options": {"num_predict": 500}}, timeout=60)
            if resp.status_code == 200:
                return {"type": "text", "message": resp.json().get("response", "")}
        except:
            pass
        return {"type": "text", "message": "服务暂时不可用"}

if __name__ == "__main__":
    agent = TenantAgent()
    print(agent.process("关键词统计"))

    # ========== URL 采集集成 ==========
    def _collect_urls(self, user_input):
        """采集 URL（使用现有 url_scout）"""
        from url_scout import URLScout
        scout = URLScout()
        
        import re
        url_match = re.search(r'https?://[^\s]+', user_input)
        if url_match:
            source_url = url_match.group()
            new_urls = scout.discover_from_seed(source_url)
            return {"type": "result", "message": f"从 {source_url} 发现 {len(new_urls)} 个新 URL"}
        
        # 默认从种子 URL 采集
        seeds = scout.load_seeds()
        total_new = 0
        for seed in seeds[:3]:
            new = scout.discover_from_seed(seed)
            total_new += len(new)
        return {"type": "result", "message": f"发现 {total_new} 个新 URL"}
    
    def _crawl_content(self, url):
        """抓取内容（使用现有 content_crawler）"""
        from content_crawler import ContentCrawler
        crawler = ContentCrawler()
        result = crawler.crawl(url)
        return {"type": "result", "message": f"已抓取 {url}", "data": result}

    # ========== URL 采集意图 ==========
    def _handle_url_command(self, user_input):
        lower = user_input.lower()
        
        # 采集 URL
        if "采集" in lower and ("url" in lower or "链接" in lower):
            return self._collect_urls(user_input)
        
        # 查看 URL 统计
        if "url统计" in lower or "链接统计" in lower:
            return self._url_stats()
        
        # 抓取内容
        if "抓取" in lower and ("内容" in lower or "页面" in lower):
            return self._crawl_content(user_input)
        
        return None
    
    def _url_stats(self):
        import json
        from pathlib import Path
        
        url_file = Path("/mnt/d/clawsjoy/data/urls/discovered.json")
        if url_file.exists():
            with open(url_file) as f:
                urls = json.load(f)
            return {"type": "result", "message": f"📊 已发现 {len(urls)} 个 URL"}
        return {"type": "result", "message": "暂无 URL 数据"}

    # ========== URL 采集意图处理 ==========
    def _handle_url_intent(self, user_input):
        lower = user_input.lower()
        
        if "采集" in lower and ("url" in lower or "链接" in lower):
            return self._trigger_url_collection()
        
        if "抓取" in lower and ("内容" in lower or "页面" in lower):
            return self._trigger_content_crawl()
        
        if "url统计" in lower or "链接统计" in lower:
            return self._get_url_stats()
        
        return None
    
    def _trigger_url_collection(self):
        """触发 URL 采集"""
        from url_scout import URLScout
        scout = URLScout()
        
        # 从种子 URL 采集
        seeds = ["https://www.immd.gov.hk/hks/", "https://www.info.gov.hk/gia/general/today.htm"]
        total = 0
        for seed in seeds:
            new = scout.discover_from_seed(seed)
            total += len(new)
        
        return {"type": "result", "message": f"✅ 发现 {total} 个新 URL"}
    
    def _trigger_content_crawl(self):
        """触发内容抓取"""
        from content_crawler import ContentCrawler
        import json
        from pathlib import Path
        
        # 获取待抓取的 URL
        url_file = Path("/mnt/d/clawsjoy/data/urls/discovered.json")
        with open(url_file) as f:
            urls = json.load(f)
        
        crawler = ContentCrawler()
        count = 0
        for url in list(urls.keys())[:5]:  # 每次抓取5个
            result = crawler.crawl(url)
            if result.get("success"):
                count += 1
        
        return {"type": "result", "message": f"✅ 已抓取 {count} 个页面"}
    
    def _get_url_stats(self):
        import json
        from pathlib import Path
        
        url_file = Path("/mnt/d/clawsjoy/data/urls/discovered.json")
        content_dir = Path("/mnt/d/clawsjoy/data/content")
        
        with open(url_file) as f:
            urls = json.load(f)
        
        content_count = len(list(content_dir.glob("*.txt"))) if content_dir.exists() else 0
        
        return {
            "type": "result",
            "message": f"📊 已发现 {len(urls)} 个 URL，已抓取 {content_count} 个页面"
        }
