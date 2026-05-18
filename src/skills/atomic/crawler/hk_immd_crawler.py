"""香港入境处专用爬虫"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.skills.atomic.crawler.smart_crawler import skill as smart_crawler

class HKImmdCrawlerSkill:
    name = "hk_immd_crawler"
    description = "香港入境事务处专用爬虫"
    version = "1.0.0"
    category = "crawler"
    
    SEED_URLS = {
        "main": "https://www.immd.gov.hk/hkt/index.html",
        "ttps": "https://www.immd.gov.hk/hkt/services/visas/Top_Talent_Pass_Scheme.html",
        "qmas": "https://www.immd.gov.hk/hkt/services/visas/Quality_Migrant_Admission_Scheme.html"
    }
    
    def execute(self, params):
        topic = params.get("topic", "ttps")
        seed_url = self.SEED_URLS.get(topic, self.SEED_URLS["ttps"])
        
        result = smart_crawler.execute({
            "seed_url": seed_url,
            "max_pages": params.get("max_pages", 3)
        })
        
        return {
            "success": result.get("success", False),
            "topic": topic,
            "seed_url": seed_url,
            "result": result,
            "message": f"香港入境处爬取完成"
        }

skill = HKImmdCrawlerSkill()
